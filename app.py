from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure MongoDB
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

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
        depot_id = data.get('depotId')
        station_master_id = data.get('stationMasterId')
        password = data.get('password')

        # Find user in DB
        user = mongo.db.depots.find_one({
            "depot_id": depot_id, 
            "station_master_id": station_master_id
        })

        if user and user['password'] == password:
            # Create session
            session['user'] = {
                "depot_id": user['depot_id'],
                "station_master_id": user['station_master_id'],
                "depot_name": user['depot_name']
            }
            return jsonify({"status": "success", "message": "Login successful"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    return render_template('login.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login_html():
    return login()

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

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
