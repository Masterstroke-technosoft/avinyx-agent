import httpx
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test():
    # Login as admin to file cases
    res = httpx.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin@city.com", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    complaints = [
        {"title": "Broken Traffic Light", "description": "The main intersection traffic light is completely out causing huge traffic.", "ward": "Downtown", "lat": 80.7128, "lon": -74.0060}, # Transport
        {"title": "Trash Not Collected", "description": "Garbage has been sitting here for 3 weeks and is smelling horrible.", "ward": "Uptown", "lat": 80.7230, "lon": -74.0162}, # Sanitation
        {"title": "Water Main Break", "description": "Water is flooding the entire street from a broken underground pipe.", "ward": "Midtown", "lat": 80.7332, "lon": -74.0264}, # Public Works
        {"title": "Vandalism and Graffiti", "description": "Someone sprayed graffiti all over the building last night.", "ward": "Downtown", "lat": 80.7434, "lon": -74.0366}, # Police
        {"title": "Dumpster Fire", "description": "The dumpster in the alley behind the restaurant is on fire!", "ward": "Uptown", "lat": 80.7536, "lon": -74.0468}, # Fire
        {"title": "Broken Playground Swings", "description": "The swings at the park are broken and dangerous for children.", "ward": "Midtown", "lat": 80.7638, "lon": -74.0570}, # Parks
    ]
    
    case_ids = []
    
    print("--- Filing 6 Department-Specific Complaints ---")
    for c in complaints:
        payload = {
            "title": c["title"],
            "description": c["description"],
            "latitude": c["lat"],
            "longitude": c["lon"],
            "ward": c["ward"],
            "priority": 1
        }
        res = httpx.post(f"{BASE_URL}/cases/", json=payload, headers=headers)
        if res.status_code == 200:
            case_id = res.json()["id"]
            case_ids.append(case_id)
            print(f"Created: {c['title']}")
        else:
            print(f"Failed to create {c['title']}: {res.text}")
            
    print("\nWaiting 15 seconds for Text & Geo Agents to analyze and Orchestrator to assign departments...")
    time.sleep(15)
    
    print("\n--- AI Department Assignments ---")
    for cid in case_ids:
        res = httpx.get(f"{BASE_URL}/cases/{cid}", headers=headers)
        if res.status_code == 200:
            data = res.json()
            dept = data.get('assigned_department')
            status = data.get('status')
            print(f"[{data['title']}]")
            print(f"   -> Assigned Dept: {dept}")
            print(f"   -> AI Severity: {data.get('ai_severity')}")
            print(f"   -> Status: {status}\n")
            
if __name__ == "__main__":
    test()
