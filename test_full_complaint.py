import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def full_test():
    print("--- Starting Full Complaint Simulation ---")
    
    # 1. Login
    email = "tester_phase8@example.com"
    password = "password123"
    res = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Submit Text Complaint
    print("\n1. Citizen submitting complaint about a massive sinkhole...")
    case_data = {
        "title": "Massive Sinkhole",
        "description": "The road completely collapsed on 5th Avenue. It's a huge sinkhole!",
        "latitude": 40.75,
        "longitude": -73.98,
        "ward": "Midtown",
        "priority": 3 # Citizen thinks it's priority 3
    }
    res = httpx.post(f"{BASE_URL}/cases/", json=case_data, headers=headers)
    case_id = res.json()["id"]
    print(f"Ticket created! Case ID: {case_id}")
    
    # 3. Upload Photo Proof
    print("\n2. Citizen uploading photo evidence of the sinkhole...")
    with open("sinkhole.jpg", "wb") as f:
        f.write(b"dummy image of a sinkhole")
    with open("sinkhole.jpg", "rb") as f:
        files = {"file": ("sinkhole.jpg", f, "image/jpeg")}
        httpx.post(f"{BASE_URL}/cases/{case_id}/media", files=files, headers=headers)
    print("Photo uploaded successfully!")
    
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
