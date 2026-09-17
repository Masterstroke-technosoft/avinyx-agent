import httpx
import json
import time
import random
BASE_URL = "http://127.0.0.1:8000/api/v1"

def full_test():
    print("--- Starting Full Complaint Simulation ---")
    
    # 1. Login
    email = "tester_phase8@example.com"
    password = "password123"
    res = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Submit Case with Media Attached
    print("\n1. Citizen submitting complaint about a massive sinkhole with a photo attached...")
    
    # Create a dummy image file
    with open("sinkhole.jpg", "wb") as f:
        f.write(b"dummy image of a sinkhole")
        
    case_data_dict = {
        "title": f"Massive Sinkhole {random.randint(1000, 9999)}",
        "description": "The road completely collapsed on 5th Avenue. It's a huge sinkhole!",
        "latitude": 40.75 + random.uniform(-0.1, 0.1),
        "longitude": -73.98 + random.uniform(-0.1, 0.1),
        "ward": "Midtown",
        "priority": 3
    }
    
    data = {
        "case_data": json.dumps(case_data_dict),
        "notify_me_via": "sms"
    }
    
    with open("sinkhole.jpg", "rb") as f:
        files = {"file": ("sinkhole.jpg", f, "image/jpeg")}
        res = httpx.post(f"{BASE_URL}/cases/", data=data, files=files, headers=headers)
        
    case_id = res.json()["id"]
    print(f"Ticket created and photo uploaded! Case ID: {case_id}")
    
    import os
    os.remove("sinkhole.jpg")
    
    # 4. Wait for AI Agents (Text, Vision, Geo) to process the RabbitMQ queues
    print("\n3. Waiting 5 seconds for the Text, Vision, and Geo Agents to process the queues...")
    time.sleep(5)
    
    # 5. Fetch Final Analysis
    print("\n4. Fetching the combined AI Analysis Report...")
    res = httpx.get(f"{BASE_URL}/cases/{case_id}/analysis", headers=headers)
    
    print("\n================ DEEP AI ANALYSIS ================")
    print(json.dumps(res.json(), indent=4))
    print("==================================================")
    
if __name__ == "__main__":
    full_test()
