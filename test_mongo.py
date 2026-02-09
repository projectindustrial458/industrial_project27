import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
uri = os.getenv("MONGO_URI")
print(f"Connecting to: {uri}")

try:
    client = MongoClient(uri)
    # The is_master command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("MongoDB connection successful!")
    
    db = client.get_default_database()
    print(f"Connected to database: {db.name}")
    
    depots_count = db.depots.count_documents({})
    print(f"Documents in 'depots' collection: {depots_count}")
    
except Exception as e:
    print(f"MongoDB connection failed: {e}")
