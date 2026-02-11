import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()

print("--- Clearing Waybills Collection ---")
db.waybills.delete_many({})
print("Waybills cleared. Master Log should now be empty.")
