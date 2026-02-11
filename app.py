from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure MongoDB
uri = os.getenv("MONGO_URI")
print(f"DEBUG: Loading MONGO_URI: {uri}")
app.config["MONGO_URI"] = uri
mongo = PyMongo(app)
print(f"DEBUG: Mongo initialized. DB: {mongo.db}")

@app.route('/')
@app.route('/index.html')
def home():
    # Check if user is logged in
    waybills = []
    if 'user' in session:
        depot_id = session['user']['depot_id']
        # Fetch waybills for this depot, sorted by most recent
        waybills = list(mongo.db.waybills.find({"depot_id": depot_id}).sort("timestamp", -1))
    
    return render_template('index.html', waybills=waybills)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        print(f"DEBUG: Login attempt for depot_id: {data.get('depotId')}, master_id: {data.get('stationMasterId')}")
        depot_id = data.get('depotId')
        station_master_id = data.get('stationMasterId')
        password = data.get('password')

        # Find user in DB
        try:
            print(f"DEBUG: Querying database for user: {station_master_id}")
            # Query by stationMasterId (case-insensitive)
            # We ignore depotId in the query for flexibility, trusting unique SM ID
            user = mongo.db.users.find_one({
                "stationMasterId": {"$regex": f"^{station_master_id}$", "$options": "i"}
            })
            print(f"DEBUG: Query result: {'User found' if user else 'User NOT found'}")
        except Exception as e:
            print(f"ERROR: Database query failed: {str(e)}")
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

        if user:
            # STRICT CHECK: Ensure the Station Master belongs to the selected Depot
            db_depot_id = user.get('depotId')
            if db_depot_id != depot_id:
                print(f"DEBUG: Depot Mismatch! User belongs to {db_depot_id} but tried to login to {depot_id}")
                return jsonify({"status": "error", "message": f"This Station Master ID belongs to {db_depot_id}, not {depot_id}. Please select the correct depot."}), 401

            if user.get('password') == password:
                # Generate platforms list if platform_count exists
                platforms = []
                if 'platform_count' in user:
                   platforms = list(range(1, int(user['platform_count']) + 1))
                elif 'platforms' in user:
                   platforms = user['platforms']
                
                # Create session
                session['user'] = {
                    "depot_id": user.get('depotId'),
                    "station_master_id": user.get('stationMasterId'),
                    "depot_name": user.get('name'),
                    "platforms": platforms
                }
                print(f"DEBUG: Login successful for {station_master_id} at {depot_id}. Session created.")
                return jsonify({
                    "status": "success", 
                    "message": "Login successful",
                    "depot_name": user.get('name'),
                    "platforms": platforms
                }), 200
            else:
                print("DEBUG: Invalid password.")
                return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        else:
            print("DEBUG: User not found.")
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    return render_template('login.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login_html():
    return login()

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/waybill', methods=['POST'])
def save_waybill():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Extract data components
        bus_reg_no = data.get('busRegNo')
        conductor_id = data.get('conductorId')
        driver_id = data.get('driverId')

        # 1. Update Bus Collection (Upsert)
        if bus_reg_no:
            mongo.db.buses.update_one(
                {"bus_reg_no": bus_reg_no},
                {"$set": {
                    "bus_reg_no": bus_reg_no,
                    "service_category": data.get('serviceCategory'),
                    "last_updated": datetime.now()
                }},
                upsert=True
            )

        # 2. Update Crew Collection - Conductor (Upsert)
        if conductor_id:
            mongo.db.crew.update_one(
                {"crew_id": conductor_id},
                {"$set": {
                    "crew_id": conductor_id,
                    "name": data.get('conductorName'),
                    "phone": data.get('conductorPhone'),
                    "role": "Conductor",
                    "last_updated": datetime.now()
                }},
                upsert=True
            )

        # 3. Update Crew Collection - Driver (Upsert)
        if driver_id:
            mongo.db.crew.update_one(
                {"crew_id": driver_id},
                {"$set": {
                    "crew_id": driver_id,
                    "name": data.get('driverName'),
                    "phone": data.get('driverPhone'),
                    "role": "Driver",
                    "last_updated": datetime.now()
                }},
                upsert=True
            )

        # 4. Save Waybill Record
        waybill_record = data.copy()
        
        # Ensure platformNumber is stored as an integer for consistent comparison
        if 'platformNumber' in waybill_record and waybill_record['platformNumber']:
            try:
                waybill_record['platformNumber'] = int(waybill_record['platformNumber'])
            except ValueError:
                pass # Keep as string if conversion fails check

        waybill_record['timestamp'] = datetime.now()
        # Add session user info if logged in
        if 'user' in session:
            waybill_record['logged_by'] = session['user']['station_master_id']
            waybill_record['depot_id'] = session['user']['depot_id']

        mongo.db.waybills.insert_one(waybill_record)

        return jsonify({"status": "success", "message": "Waybill entry logged successfully"}), 201

    except Exception as e:
        print(f"ERROR in /api/waybill: {str(e)}")
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route('/api/live-data', methods=['GET'])
def get_live_data():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    try:
        depot_id = session['user']['depot_id']
        depot_name = session['user'].get('depot_name', '')
        
        # Fetch waybills where this depot is the source OR the destination
        # We check destination against both depot_id and depot_name for robustness
        # Strict Isolation: Only show waybills created BY this depot
        # The user said "data is duplicated in all depos", implying they don't want to see incoming buses yet, 
        # or the generic destination matching was too broad. 
        # let's restrict to just records logged at this depot for now to solve the "duplication".
        # Strict Isolation: Only show waybills created BY this depot
        # LIMIT: Only show content for the CURRENT DAY (Resets at midnight)
        now = datetime.now()
        start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
        
        query = {
            "depot_id": depot_id,
            "timestamp": {"$gte": start_of_day}
        }
        
        cursor = mongo.db.waybills.find(query).sort("timestamp", -1)
        waybills = list(cursor)
        
        # Convert ObjectId to string for JSON serialization if needed, 
        # but PyMongo's jsonify usually handles it or we manually helper.
        # Let's create a clean list of dicts.
        data_list = []
        on_time_count = 0
        
        for wb in waybills:
            # Basic stats logic
            if wb.get('actualTime') and wb.get('scheduledTime'):
                if wb['actualTime'] <= wb['scheduledTime']:
                    on_time_count += 1
            
            # Prepare dict for JSON
            item = {
                "busRegNo": wb.get('busRegNo', ''),
                "serviceCategory": wb.get('serviceCategory', ''),
                "origin": wb.get('origin', ''),
                "destination": wb.get('destination', ''),
                "scheduledTime": wb.get('scheduledTime', ''),
                "actualTime": wb.get('actualTime', ''),
                "movementType": wb.get('movementType', ''),
                "platformNumber": wb.get('platformNumber', ''),
                "depot_id": wb.get('depot_id', '')
            }
            data_list.append(item)
            
        # Punctuality Score
        total = len(waybills)
        punctuality = 0
        if total > 0:
            punctuality = round((on_time_count / total) * 100, 1)
            
        # Active Fleet (approximate based on unique buses in list)
        unique_buses = set(wb.get('busRegNo') for wb in waybills)
        active_fleet = len(unique_buses)

        return jsonify({
            "status": "success",
            "waybills": data_list,
            "stats": {
                "active_fleet": active_fleet,
                "punctuality": punctuality,
                "utilization": 76 # Placeholder/Mock for now as per original design
            }
        }), 200

    except Exception as e:
        print(f"ERROR in /api/live-data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bus-history/<bus_no>', methods=['GET'])
def get_bus_history(bus_no):
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    try:
        # Fetch all waybills for this specific bus across ALL depots
        cursor = mongo.db.waybills.find({"busRegNo": bus_no}).sort("timestamp", -1)
        waybills = list(cursor)
        
        data_list = []
        for wb in waybills:
            item = {
                "busRegNo": wb.get('busRegNo', ''),
                "serviceCategory": wb.get('serviceCategory', ''),
                "origin": wb.get('origin', ''),
                "destination": wb.get('destination', ''),
                "scheduledTime": wb.get('scheduledTime', ''),
                "actualTime": wb.get('actualTime', ''),
                "movementType": wb.get('movementType', ''),
                "depot_id": wb.get('depot_id', ''),
                "platformNumber": wb.get('platformNumber', '')
            }
            data_list.append(item)
            
        return jsonify({
            "status": "success",
            "waybills": data_list
        }), 200

    except Exception as e:
        print(f"ERROR in /api/bus-history: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_records():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    try:
        # Get query parameters
        date_str = request.args.get('date')
        bus_no = request.args.get('busNo')
        depot_id = request.args.get('depotId')
        movement_type = request.args.get('movementType')
        
        # Build Query
        query = {}
        
        if bus_no:
            query["busRegNo"] = {"$regex": bus_no, "$options": "i"}
            
        if depot_id:
            query["depot_id"] = depot_id
            
        if movement_type:
            query["movementType"] = movement_type
            
        # Date filtering needs care - stored as UTC timestamps in waybills
        # For simplicity, if date is provided, we'll try to match the day
        if date_str:
            try:
                # Assuming date comes in as YYYY-MM-DD
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                start = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
                end = datetime(dt.year, dt.month, dt.day, 23, 59, 59)
                query["timestamp"] = {"$gte": start, "$lte": end}
            except ValueError:
                pass # Ignore malformed date
                
        cursor = mongo.db.waybills.find(query).sort("timestamp", -1).limit(100)
        waybills = list(cursor)
        
        data_list = []
        for wb in waybills:
            item = {
                "busRegNo": wb.get('busRegNo', ''),
                "serviceCategory": wb.get('serviceCategory', ''),
                "origin": wb.get('origin', ''),
                "destination": wb.get('destination', ''),
                "scheduledTime": wb.get('scheduledTime', ''),
                "actualTime": wb.get('actualTime', ''),
                "movementType": wb.get('movementType', ''),
                "depot_id": wb.get('depot_id', ''),
                "timestamp": wb.get('timestamp').strftime("%Y-%m-%d %H:%M") if wb.get('timestamp') else '',
                # Crew Details
                "conductorName": wb.get('conductorName', '-'),
                "conductorId": wb.get('conductorId', '-'),
                "driverName": wb.get('driverName', '-'),
                "driverId": wb.get('driverId', '-'),
                # Explicit Arrival/Departure for clarity in search
                "arrival_time": wb.get('actualTime') if wb.get('movementType') == 'Arrival' else '-',
                "departure_time": wb.get('actualTime') if wb.get('movementType') == 'Departure' else '-'
            }
            data_list.append(item)
            
        return jsonify({
            "status": "success",
            "count": len(data_list),
            "waybills": data_list
        }), 200

    except Exception as e:
        print(f"ERROR in /api/search: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/master-log', methods=['GET'])
def get_master_log():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    try:
        depot_id = session['user']['depot_id']
        
        # Current Date Range
        now = datetime.now()
        start = datetime(now.year, now.month, now.day, 0, 0, 0)
        end = datetime(now.year, now.month, now.day, 23, 59, 59)
        
        # Fetch all waybills for THIS depot today
        cursor = mongo.db.waybills.find({
            "depot_id": depot_id,
            "timestamp": {"$gte": start, "$lte": end}
        }).sort("scheduledTime", 1)
        
        waybills = list(cursor)
        
        data_list = []
        for wb in waybills:
            # Determine status
            status = "On Time"
            status_class = "bg-success"
            
            if wb.get('actualTime') > wb.get('scheduledTime'):
                status = "Delayed"
                status_class = "bg-danger"
            elif not wb.get('actualTime'):
                status = "Scheduled"
                status_class = "bg-info"

            data_list.append({
                "busRegNo": wb.get('busRegNo', ''),
                "serviceCategory": wb.get('serviceCategory', ''),
                "route": f"{wb.get('origin', '')} - {wb.get('destination', '')}",
                "scheduledTime": wb.get('scheduledTime', ''),
                "actualTime": wb.get('actualTime', '-'),
                "movementType": wb.get('movementType', ''),
                "status": status,
                "statusClass": status_class,
                "alerts": "PF-" + str(wb.get('platformNumber', '-'))
            })
            
        return jsonify({
            "status": "success",
            "date": now.strftime("%b %d, %Y"),
            "waybills": data_list
        }), 200
        
    except Exception as e:
        print(f"ERROR in /api/master-log: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test_db')
def test_db():
    try:
        # User flask_pymongo to ping the database
        mongo.db.command('ping')
        return jsonify({"status": "success", "message": "Connected to MongoDB!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/search/bus', methods=['GET'])
def search_bus():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    results = mongo.db.buses.find(
        {"bus_reg_no": {"$regex": query, "$options": "i"}},
        {"_id": 0, "bus_reg_no": 1, "service_category": 1}
    ).limit(10)
    
    return jsonify(list(results))

@app.route('/api/search/place', methods=['GET'])
def search_place():
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    query = request.args.get('q', '')
    if not query:
        return jsonify([])

    # Search in places collection
    results = mongo.db.places.find(
        {"name": {"$regex": query, "$options": "i"}},
        {"_id": 0, "name": 1, "code": 1}
    ).limit(10)
    
    return jsonify(list(results))

@app.route('/api/crew/<crew_id>', methods=['GET'])
def get_crew_details(crew_id):
    if 'user' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    crew = mongo.db.crew.find_one({"crew_id": crew_id}, {"_id": 0})
    
    if crew:
        return jsonify({"status": "success", "crew": crew})
    else:
        return jsonify({"status": "error", "message": "Crew not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
