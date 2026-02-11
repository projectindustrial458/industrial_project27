import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()

print("--- Clearing Users Collection ---")
db.users.delete_many({})

# List of KSRTC Depots (Codes and Names)
depots = [
    # Thiruvananthapuram
    {"code": "TVM", "name": "Thiruvananthapuram Central"},
    {"code": "CTY", "name": "Thiruvananthapuram City"},
    {"code": "PPD", "name": "Pappanamcode"},
    {"code": "VZM", "name": "Vizhinjam"},
    {"code": "NDD", "name": "Nedumangad"},
    {"code": "NTA", "name": "Neyyattinkara"},
    {"code": "ATL", "name": "Attingal"},
    {"code": "VJR", "name": "Vellarada"},
    {"code": "PRS", "name": "Parassala"},
    {"code": "KZM", "name": "Kazhakkuttam"}, # Often associated with TVM

    # Kollam
    {"code": "KLM", "name": "Kollam"},
    {"code": "KTR", "name": "Kottarakkara"},
    {"code": "KPN", "name": "Karunagappally"},
    {"code": "PVR", "name": "Punalur"},
    {"code": "CHT", "name": "Chadayamangalam"},
    {"code": "PYR", "name": "Pathanapuram"},
    {"code": "ARY", "name": "Aryankavu"},

    # Pathanamthitta
    {"code": "PTA", "name": "Pathanamthitta"},
    {"code": "ADOOR", "name": "Adoor"}, # Code often ADR or ADOOR
    {"code": "TVL", "name": "Thiruvalla"},
    {"code": "RNI", "name": "Ranni"},
    {"code": "KNI", "name": "Konni"},
    {"code": "MDY", "name": "Mallappally"},

    # Alappuzha
    {"code": "ALP", "name": "Alappuzha"},
    {"code": "CGR", "name": "Chengannur"},
    {"code": "KYM", "name": "Kayamkulam"},
    {"code": "CTL", "name": "Cherthala"},
    {"code": "HRD", "name": "Haripad"},
    {"code": "MVK", "name": "Mavelikkara"},
    {"code": "EDY", "name": "Edathua"},

    # Kottayam
    {"code": "KTYM", "name": "Kottayam"},
    {"code": "CHR", "name": "Changanassery"},
    {"code": "PLA", "name": "Pala"},
    {"code": "ETP", "name": "Erattupetta"},
    {"code": "VKP", "name": "Vaikom"},
    {"code": "PNK", "name": "Ponkunnam"},
    
    # Idukki
    {"code": "TDP", "name": "Thodupuzha"},
    {"code": "KML", "name": "Kumily"},
    {"code": "MNR", "name": "Munnar"},
    {"code": "KTP", "name": "Kattappana"},
    {"code": "NQM", "name": "Nedumkandam"},

    # Ernakulam
    {"code": "ERS", "name": "Ernakulam"},
    {"code": "ALY", "name": "Aluva"},
    {"code": "PBR", "name": "Perumbavoor"},
    {"code": "MVP", "name": "Muvattupuzha"},
    {"code": "KTMG", "name": "Kothamangalam"},
    {"code": "NPT", "name": "North Paravur"},
    {"code": "ANG", "name": "Angamaly"},
    {"code": "PVR", "name": "Piravom"},
    {"code": "KTR", "name": "Koothattukulam"},

    # Thrissur
    {"code": "TSR", "name": "Thrissur"},
    {"code": "CKD", "name": "Chalakudy"},
    {"code": "IJK", "name": "Irinjalakuda"},
    {"code": "KDG", "name": "Kodungallur"},
    {"code": "GVY", "name": "Guruvayoor"},
    {"code": "MKD", "name": "Mala"},

    # Palakkad
    {"code": "PGT", "name": "Palakkad"},
    {"code": "PLK", "name": "Palakkad"}, # Duplicate code sometimes used
    {"code": "CHT", "name": "Chittur"},
    {"code": "MNR", "name": "Mannarkkad"}, # Conflict with Munnar? MGD?
    {"code": "VDR", "name": "Vadakkencherry"},

    # Malappuram
    {"code": "MPM", "name": "Malappuram"},
    {"code": "PMN", "name": "Perinthalmanna"},
    {"code": "NNM", "name": "Nilambur"},
    {"code": "PNI", "name": "Ponnani"},

    # Kozhikode
    {"code": "KKD", "name": "Kozhikode"},
    {"code": "TAM", "name": "Thamarassery"},
    {"code": "VDK", "name": "Vadakara"},

    # Wayanad
    {"code": "SBY", "name": "Sulthan Bathery"},
    {"code": "KPT", "name": "Kalpetta"},
    {"code": "MDY", "name": "Mananthavady"},

    # Kannur
    {"code": "KNR", "name": "Kannur"},
    {"code": "TLY", "name": "Thalassery"},
    {"code": "PAY", "name": "Payyannur"},

    # Kasaragod
    {"code": "KGD", "name": "Kasaragod"},
    {"code": "KJN", "name": "Kanhangad"}
]

print(f"--- Seeding {len(depots)} Depots ---")

for depot in depots:
    depot_id = depot['code'].upper()
    
    # Standardize Station Master ID and Password
    # Example: SM_TVM_001, ksrtc_tvm_001
    sm_id = f"SM_{depot_id}_001"
    password = f"ksrtc_{depot_id.lower()}_001"
    
    user_data = {
        "depotId": depot_id,
        "name": f"Station Master - {depot['name']}",
        "stationMasterId": sm_id,
        "password": password,
        "platform_count": 20 # User default
    }
    
    try:
        db.users.update_one(
            {"stationMasterId": sm_id},
            {"$set": user_data},
            upsert=True
        )
        print(f"Upserted: {depot_id} | {sm_id} | {password}")
    except Exception as e:
        print(f"Error seeding {depot_id}: {e}")

print("\n--- Seeding Complete ---")
print("Total Users:", db.users.count_documents({}))
