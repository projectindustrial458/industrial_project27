import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("Error: MONGO_URI not found in .env file.")
    exit(1)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client.get_database() # Uses the database from the URI

print(f"Connected to database: {db.name}")

# --- Seed Data ---

# 1. Buses
buses = [
    {"bus_reg_no": "KL-15-A-1102", "service_category": "Super Fast", "type": "Leyland"},
    {"bus_reg_no": "KL-15-A-1205", "service_category": "Fast Passenger", "type": "Eicher"},
    {"bus_reg_no": "KL-15-H-9876", "service_category": "Ordinary", "type": "Tata"},
    {"bus_reg_no": "KL-15-A-4321", "service_category": "Minnal", "type": "Scania"},
    {"bus_reg_no": "KL-15-A-5555", "service_category": "Super Deluxe", "type": "Volvo"},
    {"bus_reg_no": "KL-15-A-6789", "service_category": "Low Floor AC", "type": "Volvo"},
    {"bus_reg_no": "KL-15-A-1111", "service_category": "Ordinary", "type": "Leyland"},
    {"bus_reg_no": "KL-15-A-2222", "service_category": "Fast Passenger", "type": "Tata"},
    {"bus_reg_no": "KL-15-A-3333", "service_category": "Super Fast", "type": "Leyland"},
    {"bus_reg_no": "KL-15-A-4444", "service_category": "Super Express", "type": "Eicher"},
    {"bus_reg_no": "KL-15-A-7777", "service_category": "Swift Deluxe", "type": "Ashok Leyland"},
    {"bus_reg_no": "KL-15-A-8888", "service_category": "City Fast", "type": "Tata"},
    {"bus_reg_no": "KL-15-A-9999", "service_category": "Ordinary", "type": "Eicher"},
    {"bus_reg_no": "KL-15-A-1010", "service_category": "Super Fast", "type": "Leyland"},
    {"bus_reg_no": "KL-15-A-2020", "service_category": "Fast Passenger", "type": "Tata"},
    {"bus_reg_no": "KL-15-A-3030", "service_category": "Ordinary", "type": "Leyland"},
    {"bus_reg_no": "KL-15-A-4040", "service_category": "Super Deluxe", "type": "Volvo"},
    {"bus_reg_no": "KL-15-A-5050", "service_category": "Minnal", "type": "Scania"},
    {"bus_reg_no": "KL-15-A-6060", "service_category": "Super Express", "type": "Eicher"},
    {"bus_reg_no": "KL-15-A-7070", "service_category": "Ordinary", "type": "Tata"}
]

# 2. Crew (Conductors and Drivers)
crew_members = [
    # Conductors
    {"crew_id": "C1001", "name": "Rajesh Kumar", "role": "Conductor", "phone": "9876543210"},
    {"crew_id": "C1002", "name": "Suresh Babu", "role": "Conductor", "phone": "9876543211"},
    {"crew_id": "C1003", "name": "Manoj P", "role": "Conductor", "phone": "9876543212"},
    {"crew_id": "C1004", "name": "Vinu Thomas", "role": "Conductor", "phone": "9876543213"},
    {"crew_id": "C1005", "name": "Anil K", "role": "Conductor", "phone": "9876543214"},
    {"crew_id": "C1006", "name": "Biju M", "role": "Conductor", "phone": "9876543215"},
    {"crew_id": "C1007", "name": "Jose Varghese", "role": "Conductor", "phone": "9876543216"},
    {"crew_id": "C1008", "name": "Sunil Dutt", "role": "Conductor", "phone": "9876543217"},
    {"crew_id": "C1009", "name": "Praveen S", "role": "Conductor", "phone": "9876543218"},
    {"crew_id": "C1010", "name": "Deepak R", "role": "Conductor", "phone": "9876543219"},

    # Drivers
    {"crew_id": "D2001", "name": "Mohan Lal", "role": "Driver", "phone": "8765432109"},
    {"crew_id": "D2002", "name": "Mammootty K", "role": "Driver", "phone": "8765432108"},
    {"crew_id": "D2003", "name": "Jayan V", "role": "Driver", "phone": "8765432107"},
    {"crew_id": "D2004", "name": "Prem Nazir", "role": "Driver", "phone": "8765432106"},
    {"crew_id": "D2005", "name": "Dileep G", "role": "Driver", "phone": "8765432105"},
    {"crew_id": "D2006", "name": "Jayaram S", "role": "Driver", "phone": "8765432104"},
    {"crew_id": "D2007", "name": "Prithviraj S", "role": "Driver", "phone": "8765432103"},
    {"crew_id": "D2008", "name": "Indrajith S", "role": "Driver", "phone": "8765432102"},
    {"crew_id": "D2009", "name": "Fahad F", "role": "Driver", "phone": "8765432101"},
    {"crew_id": "D2010", "name": "Nivin P", "role": "Driver", "phone": "8765432100"}
]

# 3. Places (For Autocomplete)
places = [
    {"name": "Thiruvananthapuram", "code": "TVM"},
    {"name": "Kollam", "code": "KLM"},
    {"name": "Alappuzha", "code": "ALP"},
    {"name": "Pathanamthitta", "code": "PTA"},
    {"name": "Kottayam", "code": "KTYM"},
    {"name": "Idukki", "code": "IDK"},
    {"name": "Ernakulam", "code": "EKM"},
    {"name": "Thrissur", "code": "TCR"},
    {"name": "Palakkad", "code": "PKD"},
    {"name": "Malappuram", "code": "MLP"},
    {"name": "Kozhikode", "code": "KKD"},
    {"name": "Wayanad", "code": "WYD"},
    {"name": "Kannur", "code": "KNR"},
    {"name": "Kasaragod", "code": "KSD"},
    {"name": "Kumily", "code": "KML"},
    {"name": "Munnar", "code": "MNR"},
    {"name": "Guruvayur", "code": "GVR"},
    {"name": "Bengaluru", "code": "BLR"},
    {"name": "Mysuru", "code": "MYS"},
    {"name": "Coimbatore", "code": "CBE"}
]

# --- Insert Data ---

# Buses
print("Seeding Buses...")
for bus in buses:
    db.buses.update_one(
        {"bus_reg_no": bus["bus_reg_no"]},
        {"$set": bus},
        upsert=True
    )
print(f"Upserted {len(buses)} buses.")

# Crew
print("Seeding Crew...")
for crew in crew_members:
    db.crew.update_one(
        {"crew_id": crew["crew_id"]},
        {"$set": crew},
        upsert=True
    )
print(f"Upserted {len(crew_members)} crew members.")

# Places
print("Seeding Places...")
for place in places:
    db.places.update_one(
        {"name": place["name"]},
        {"$set": place},
        upsert=True
    )
print(f"Upserted {len(places)} places.")

print("\nDatabase seeding complete!")
