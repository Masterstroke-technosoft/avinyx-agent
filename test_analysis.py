import httpx
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def fetch_analysis():
    print("--- Fetching Deep AI Analysis ---")
    
    # 1. Login to get token (using the emergency tester from earlier)
    email = "tester_phase8@example.com"
    password = "password123"
    res = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if res.status_code != 200:
        print("Login failed! Did you run test_phase8_emergency.py yet?")
        return
        
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get my cases to find a case_id
    res = httpx.get(f"{BASE_URL}/cases/me", headers=headers)
    cases = res.json()
    if not cases:
        print("No cases found for this user.")
        return
        
    case_id = cases[0]["id"]
    print(f"Found Case ID: {case_id}")
    
    # 3. Fetch the deep analysis
    print("\nRequesting AI Analysis from Server...")
    res = httpx.get(f"{BASE_URL}/cases/{case_id}/analysis", headers=headers)
    
    print("\n--- DEEP AI ANALYSIS REPORT ---")
    print(json.dumps(res.json(), indent=4))
    
if __name__ == "__main__":
    fetch_analysis()
