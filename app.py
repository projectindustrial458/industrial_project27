from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from datetime import datetime
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
    # Check if user is logged in via session in frontend, 
    # but for now just serve the index page.
    # In a real app, you might redirect to login if not authenticated.
    return render_template('index.html')

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
            print(f"DEBUG: Querying database for user: {station_master_id} in depot: {depot_id}")
            user = mongo.db.depots.find_one({
                "depot_id": depot_id, 
                "station_master_id": station_master_id
            })
            print(f"DEBUG: Query result: {'User found' if user else 'User NOT found'}")
        except Exception as e:
            print(f"ERROR: Database query failed: {str(e)}")
            return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

        if user and user['password'] == password:
            # Create session
            session['user'] = {
                "depot_id": user['depot_id'],
                "station_master_id": user['station_master_id'],
                "depot_name": user['depot_name']
            }
            print("DEBUG: Login successful, session created.")
            return jsonify({"status": "success", "message": "Login successful"}), 200
        else:
            print("DEBUG: Invalid credentials.")
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
                    "last_updated": datetime.utcnow()
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
                    "last_updated": datetime.utcnow()
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
                    "last_updated": datetime.utcnow()
                }},
                upsert=True
            )

        # 4. Save Waybill Record
        waybill_record = data.copy()
        waybill_record['timestamp'] = datetime.utcnow()
        # Add session user info if logged in
        if 'user' in session:
            waybill_record['logged_by'] = session['user']['station_master_id']
            waybill_record['depot_id'] = session['user']['depot_id']

        mongo.db.waybills.insert_one(waybill_record)

        return jsonify({"status": "success", "message": "Waybill entry logged successfully"}), 201

    except Exception as e:
        print(f"ERROR in /api/waybill: {str(e)}")
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

@app.route('/test_db')
def test_db():
    try:
        # User flask_pymongo to ping the database
        mongo.db.command('ping')
        return jsonify({"status": "success", "message": "Connected to MongoDB!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
