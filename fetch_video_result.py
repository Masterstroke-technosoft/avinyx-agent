import httpx
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Login to get token
login_data = {"username": "admin@city.com", "password": "admin123"}
response = httpx.post(f"{BASE_URL}/auth/login", data=login_data)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

case_id = "e85bd44f-cfba-452f-a4c2-8b73817b63ea"

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
