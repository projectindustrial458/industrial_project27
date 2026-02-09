from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri)
db = client.get_database("industrial_project")

def check_collections():
    print("--- Collection Status ---")
    
    # Check waybills
    waybills_count = db.waybills.count_documents({})
    print(f"Waybills: {waybills_count}")
    last_waybill = db.waybills.find_one(sort=[("_id", -1)])
    if last_waybill:
        print(f"  Latest Waybill Bus: {last_waybill.get('busRegNo')}")
        print(f"  Route: {last_waybill.get('origin')} -> {last_waybill.get('destination')}")
        print(f"  Platform: {last_waybill.get('platformNumber')}")

    # Check buses
    buses_count = db.buses.count_documents({})
    print(f"Buses: {buses_count}")
    bus = db.buses.find_one({"bus_reg_no": "KL-15-A-9999"})
    if bus:
        print(f"  Found Test Bus: {bus.get('bus_reg_no')}")

    # Check crew
    crew_count = db.crew.count_documents({})
    print(f"Crew: {crew_count}")
    conductor = db.crew.find_one({"crew_id": "C1001"})
    driver = db.crew.find_one({"crew_id": "D2001"})
    if conductor:
        print(f"  Found Conductor: {conductor.get('name')}")
    if driver:
        print(f"  Found Driver: {driver.get('name')}")

if __name__ == "__main__":
    check_collections()
