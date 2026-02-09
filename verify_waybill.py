import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_waybill_submission():
    payload = {
        "busRegNo": "KL-15-A-9999",
        "serviceCategory": "RTC",
        "movementType": "Departure",
        "origin": "TVM",
        "destination": "ERS",
        "viaRoute": "Kollam, Alappuzha",
        "platformNumber": "04",
        "scheduledTime": "08:00",
        "actualTime": "08:15",
        "conductorName": "Test Conductor",
        "conductorId": "C1001",
        "conductorPhone": "9876543210",
        "driverName": "Test Driver",
        "driverId": "D2001",
        "driverPhone": "9123456789"
    }

    print(f"Submitting waybill for bus {payload['busRegNo']}...")
    try:
        response = requests.post(f"{BASE_URL}/api/waybill", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("SUCCESS: Waybill submitted successfully.")
        else:
            print("FAILURE: Submission failed.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_waybill_submission()
