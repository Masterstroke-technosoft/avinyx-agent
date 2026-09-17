import httpx
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Login to get token
login_data = {"username": "admin@city.com", "password": "admin123"}
response = httpx.post(f"{BASE_URL}/auth/login", data=login_data)
if response.status_code != 200:
    print("Login failed! Did you run create_departments.py?")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Create the Complaint
print("Filing water logging complaint...")
complaint = {
    "title": "Severe Water Logging",
    "description": "The entire street is flooded due to a massive water leak. Cars cannot pass.",
    "ward": "Midtown",
    "lat": 90.1234, # Unique coordinate to bypass geo-deduplication
    "lon": -74.1234
}

res = httpx.post(f"{BASE_URL}/cases/", json=complaint, headers=headers)
case = res.json()
case_id = case["id"]
print(f"Created Case: {case_id}")

# 3. Upload the Video
print("Uploading video evidence...")
video_path = r"C:\Users\Masterstroke\Downloads\14910244-uhd_3840_2160_30fps.mp4"
with open(video_path, "rb") as f:
    files = {"file": ("video.mp4", f, "video/mp4")}
    upload_res = httpx.post(f"{BASE_URL}/cases/{case_id}/media", headers=headers, files=files)
    
print("Video uploaded:", upload_res.json())

# 4. Wait for processing
print("Waiting 30 seconds for AI processing (Vision, Text, Geo -> Orchestrator)...")
time.sleep(30)

# 5. Fetch final status
final_res = httpx.get(f"{BASE_URL}/cases/{case_id}", headers=headers)
final_case = final_res.json()
print("\n--- Final AI Assignment ---")
print(f"Assigned Dept: {final_case.get('assigned_department')}")
print(f"AI Severity: {final_case.get('ai_severity')}")
print(f"Status: {final_case.get('status')}")

# Fetch analysis report
analysis = httpx.get(f"{BASE_URL}/cases/{case_id}/analysis", headers=headers)
print("\n--- Detailed AI Analysis ---")
print(json.dumps(analysis.json(), indent=2))
