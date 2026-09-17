import httpx
import time
import random

BASE_URL = "http://127.0.0.1:8000/api/v1"

def create_case(client, token, title, description):
    headers = {"Authorization": f"Bearer {token}"}
    case_data = {
        "title": f"{title} - {random.randint(1000, 9999)}",
        "description": description,
        "latitude": 40.7128 + random.uniform(-0.1, 0.1),
        "longitude": -74.0060 + random.uniform(-0.1, 0.1),
        "ward": f"Ward {random.randint(1, 10)}"
    }
    response = client.post(f"{BASE_URL}/cases/", json=case_data, headers=headers)
    return response.json()

def run_test():
    with httpx.Client(timeout=30.0) as client:
        # 1. Register a test citizen
        email = f"test_citizen_{int(time.time())}@example.com"
        password = "password123"
        client.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
        
        # 2. Login
        res = client.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
        token = res.json()["access_token"]
        
        print("Submitting Case 1 (Should route to Transportation -> Pratham)...")
        create_case(client, token, "Massive pothole on the highway", "There is a huge pothole causing traffic and accidents on the main road.")
        
        print("Submitting Case 2 (Should route to Water Dept -> Adityaa)...")
        create_case(client, token, "Major water pipe burst", "A main water line has broken and is flooding the entire street, please fix it immediately.")
        
        print("Submitting Case 3 (Should route to Sanitation -> Aditya Isadkar)...")
        create_case(client, token, "Illegal garbage dumping", "A large truck dumped toxic waste and garbage in the middle of the public park.")
        
        print("\nAll 3 cases submitted! The background AI agents are now analyzing them.")
        print("Check your Uvicorn terminal for the email dispatch logs, and check your real inboxes!")

if __name__ == "__main__":
    run_test()
