import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"
IMAGE_PATH = r"C:\Users\Masterstroke\Downloads\p1.jpg"

def mass_test():
    print("--- Starting Mass Complaint Stress Test (10 Tickets) ---")
    
    # 1. Login
    email = "tester_phase8@example.com"
    password = "password123"
    res = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if res.status_code != 200:
        print("Login failed! Did you restart the server?")
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    case_ids = []
    
    # 2. Fire 10 tickets at the exact same location
    print("\n1. Citizens are rapidly submitting 10 tickets for the exact same pothole...")
    for i in range(1, 11):
        case_data = {
            "title": f"Massive Pothole Report #{i}",
            "description": "This pothole is destroying tires!",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "ward": "Downtown",
            "priority": 3
        }
        res = httpx.post(f"{BASE_URL}/cases/", json=case_data, headers=headers)
        case_id = res.json()["id"]
        case_ids.append(case_id)
        print(f"Ticket {i}/10 created! ID: {case_id}")
        
        # Upload the user's provided photo
        try:
            with open(IMAGE_PATH, "rb") as f:
                files = {"file": ("p1.jpg", f, "image/jpeg")}
                httpx.post(f"{BASE_URL}/cases/{case_id}/media", files=files, headers=headers)
        except Exception as e:
            print(f"Failed to upload image for Ticket {i}: {e}")
            
    # 3. Wait for AI Agents to process the queues
    print("\n2. Waiting 10 seconds for the AI Agents to chew through the RabbitMQ queues...")
    time.sleep(10)
    
    # 4. Fetch the Deep Analysis for the 10th ticket
    last_case = case_ids[-1]
    print(f"\n3. Fetching the combined AI Analysis Report for the 10th Ticket ({last_case})...")
    res = httpx.get(f"{BASE_URL}/cases/{last_case}/analysis", headers=headers)
    
    print("\n================ DEEP AI ANALYSIS (Ticket #10) ================")
    print(json.dumps(res.json(), indent=4))
    print("===============================================================")
    
if __name__ == "__main__":
    mass_test()
