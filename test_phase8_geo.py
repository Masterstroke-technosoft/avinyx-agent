import httpx
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_geo():
    print("--- Testing Geo-Analytics Agent ---")
    
    # 1. Login
    email = "tester_geo@example.com"
    password = "password123"
    httpx.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    res = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Submit multiple tickets at the exact same coordinates
    case_data = {
        "title": "Pothole",
        "description": "Big pothole on the street.",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ward": "Downtown",
        "priority": 3
    }
    
    print("Submitting Ticket 1 (Original)...")
    httpx.post(f"{BASE_URL}/cases/", json=case_data, headers=headers)
    time.sleep(1)
    
    print("Submitting Ticket 2 (Duplicate)...")
    httpx.post(f"{BASE_URL}/cases/", json=case_data, headers=headers)
    time.sleep(1)
    
    print("Submitting Ticket 3 (Duplicate)...")
    httpx.post(f"{BASE_URL}/cases/", json=case_data, headers=headers)
    
    print("\nTickets submitted! Check the Geo Agent terminal to see it detect the duplicates!")
    
if __name__ == "__main__":
    test_geo()
