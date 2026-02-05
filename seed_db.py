from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import random
import string
import os

load_dotenv()

app = Flask(__name__)
# Adjust URI if your local mongo is different
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_station_master_id():
    return f"SM{random.randint(1000, 9999)}"

depots = [
    {"code": "TVM", "name": "Thiruvananthapuram Central"},
    {"code": "KML", "name": "Kumily"},
    {"code": "ALP", "name": "Alappuzha"},
    {"code": "KTYM", "name": "Kottayam"},
    {"code": "ERS", "name": "Ernakulam"},
    {"code": "TSR", "name": "Thrissur"},
    {"code": "PGT", "name": "Palakkad"},
    {"code": "KKD", "name": "Kozhikode"},
    {"code": "KNR", "name": "Kannur"},
    {"code": "KGD", "name": "Kasaragod"},
    {"code": "OTHER", "name": "Other Depot"}
]

def seed_data():
    with app.app_context():
        # Clear existing
        mongo.db.depots.delete_many({})
        
        created_data = []

        print(f"{'DEPOT':<10} | {'USERNAME (ID)':<15} | {'PASSWORD':<15}")
        print("-" * 45)

        for depot in depots:
            station_master_id = generate_station_master_id()
            password = generate_password()
            
            doc = {
                "depot_id": depot['code'],
                "depot_name": depot['name'],
                "station_master_id": station_master_id,
                "password": password # In production, hash this!
            }
            
            mongo.db.depots.insert_one(doc)
            created_data.append(doc)
            
            print(f"{depot['code']:<10} | {station_master_id:<15} | {password:<15}")

        print("-" * 45)
        print("Database seeded successfully with random credentials.")

if __name__ == "__main__":
    seed_data()
