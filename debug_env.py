import os
from dotenv import load_dotenv
load_dotenv()
print(f"MONGO_URI: {os.getenv('MONGO_URI')}")
