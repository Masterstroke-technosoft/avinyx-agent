import httpx
import os
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_orchestrator():
    print("--- Starting Phase 7 Orchestrator Test ---")
    
    # 1. Login/Register
    email = "tester_phase7@example.com"
    password = "password123"
    httpx.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
    res = httpx.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create Case
    case_data = {
        "title": "Broken Streetlight",
        "description": "It is completely shattered.",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "ward": "Uptown",
        "priority": 5
    }
    res = httpx.post(f"{BASE_URL}/cases/", json=case_data, headers=headers)
    case_id = res.json()["id"]
    print(f"Created Case: {case_id}")
    
    # 3. Upload Media (This should trigger the Orchestrator)
    with open("dummy_vision.jpg", "wb") as f:
        f.write(b"dummy image")
    with open("dummy_vision.jpg", "rb") as f:
        files = {"file": ("dummy_vision.jpg", f, "image/jpeg")}
        res = httpx.post(f"{BASE_URL}/cases/{case_id}/media", files=files, headers=headers)
    print("Media Uploaded.")
    os.remove("dummy_vision.jpg")
    
    # 4. Check for Pending Tasks (As if we are the AI)
    # The AI does not need standard user auth to poll tasks, but currently our endpoint is not protected by auth anyway
    res = httpx.get(f"{BASE_URL}/agent-tasks/pending?agent_type=vision")
    tasks = res.json()
    print(f"Pending Tasks Found: {len(tasks)}")
    
    if len(tasks) == 0:
        print("ERROR: No AgentTask was spawned!")
        return
        
    task_id = tasks[0]["id"]
    print(f"Task ID spawned: {task_id}")
    
    # 5. Submit AI Result (Simulating a severity of 8)
    ai_result = {
        "status": "completed",
        "result_data": {"severity": 8, "confidence": 0.95, "tags": ["shattered", "glass", "hazard"]}
    }
    res = httpx.post(f"{BASE_URL}/agent-tasks/{task_id}/result", json=ai_result)
    print(f"AI Result Submitted. Status Code: {res.status_code}")
    
    # 6. Verify Workflow State Machine
    res = httpx.get(f"{BASE_URL}/cases/{case_id}", headers=headers)
    updated_case = res.json()
    new_status = updated_case["status"]
    print(f"Original Case Status: pending")
    print(f"Updated Case Status: {new_status}")
    
    if new_status == "requires_dispatch":
        print("SUCCESS! The Orchestrator automatically updated the case status based on AI feedback.")
    else:
        print("FAILED! The Orchestrator did not update the case status.")

if __name__ == "__main__":
    test_orchestrator()
