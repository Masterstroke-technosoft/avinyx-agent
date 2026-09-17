import httpx
import os

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_api():
    # 1. Register a new test user to ensure clean state
    email = "tester_phase6@example.com"
    password = "password123"
    
    # Try register, if exists ignore
    res = httpx.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    print("Register:", res.status_code, res.text)
    
    # 2. Login
    res = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    print("Login:", res.status_code)
    if res.status_code != 200:
        print("Login failed, aborting test.", res.text)
        return
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create a case
    case_data = {
        "title": "Pothole on Main St",
        "description": "Huge pothole near the intersection",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ward": "Downtown",
        "priority": 5
    }
    res = httpx.post(f"{BASE_URL}/cases/", json=case_data, headers=headers)
    print("Create Case:", res.status_code, res.text)
    if res.status_code != 200:
        print("Case creation failed, aborting test.")
        return
        
    case_id = res.json()["id"]
    
    # 4. Upload media
    # Create a dummy image file
    with open("dummy.jpg", "wb") as f:
        f.write(b"dummy image content")
        
    with open("dummy.jpg", "rb") as f:
        files = {"file": ("dummy.jpg", f, "image/jpeg")}
        res = httpx.post(f"{BASE_URL}/cases/{case_id}/media", files=files, headers=headers)
    print("Upload Media:", res.status_code, res.text)
    
    # Clean up dummy file
    if os.path.exists("dummy.jpg"):
        os.remove("dummy.jpg")
        
    # 5. Get My Cases
    res = httpx.get(f"{BASE_URL}/cases/me", headers=headers)
    print("Get My Cases:", res.status_code, len(res.json()), "cases found")
    
if __name__ == "__main__":
    test_api()
