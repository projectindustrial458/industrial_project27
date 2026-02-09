from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import argparse

load_dotenv()

app = Flask(__name__)
# Configure MongoDB
uri = os.getenv("MONGO_URI")
if not uri:
    print("Error: MONGO_URI not found in environment variables.")
    exit(1)

app.config["MONGO_URI"] = uri
mongo = PyMongo(app)

def create_user(depot_id, depot_name, station_master_id, password):
    with app.app_context():
        # Check if user already exists
        existing_user = mongo.db.depots.find_one({
            "depot_id": depot_id,
            "station_master_id": station_master_id
        })

        if existing_user:
            print(f"User with Station Master ID '{station_master_id}' at Depot '{depot_id}' already exists.")
            return

        new_user = {
            "depot_id": depot_id,
            "depot_name": depot_name,
            "station_master_id": station_master_id,
            "password": password  # In a real app, hash this!
        }

        try:
            mongo.db.depots.insert_one(new_user)
            print(f"Successfully created user:\nDepot: {depot_name} ({depot_id})\nStation Master ID: {station_master_id}\nPassword: {password}")
        except Exception as e:
            print(f"Error creating user: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new user in the database.")
    parser.add_argument("--depot_id", required=True, help="Depot ID (e.g., TVM)")
    parser.add_argument("--depot_name", required=True, help="Depot Name (e.g., Thiruvananthapuram Central)")
    parser.add_argument("--sm_id", required=True, help="Station Master ID")
    parser.add_argument("--password", required=True, help="Password")

    args = parser.parse_args()

    create_user(args.depot_id, args.depot_name, args.sm_id, args.password)
