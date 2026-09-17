import httpx
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def trigger_emergency():
    print("--- Triggering Phase 8 Emergency Test ---")
    
    # 1. Login
    email = "tester_phase8@example.com"
    password = "password123"
    httpx.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    res = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create a Highly Severe Ticket
    print("Submitting a ticket for a fallen live power line...")
    case_data = {
        "title": "EMERGENCY: LIVE POWER LINE DOWN",
        "description": "A tree fell and knocked down a live power line on Main St. It is sparking and highly dangerous!",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ward": "Downtown",
        "priority": 5
    }
    
    # The moment this hits the API, the Orchestrator publishes to the text_queue
    res = httpx.post(f"{BASE_URL}/cases/", json=case_data, headers=headers)
    if res.status_code != 200:
        print(f"Failed to submit ticket: {res.text}")
        return
        
    case_id = res.json()["id"]
    print(f"Ticket Submitted! Case ID: {case_id}")
    print("Check the terminal windows for the Text Agent and Critical Agent to see the automated response!")
    
if __name__ == "__main__":
    trigger_emergency()
