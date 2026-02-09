import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
uri = os.getenv("MONGO_URI")
client = MongoClient(uri)
db = client.get_default_database()

print(f"{'DEPOT ID':<10} | {'MASTER ID':<15} | {'PASSWORD':<15}")
print("-" * 45)
for doc in db.depots.find():
    print(f"{doc.get('depot_id'):<10} | {doc.get('station_master_id'):<15} | {doc.get('password'):<15}")
