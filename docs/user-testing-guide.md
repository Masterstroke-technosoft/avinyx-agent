# User Testing Guide (Developer & QA)

This document is designed to help developers and QA engineers test the Civic System API from the perspective of its primary end-users: **Citizens** and **Department Officials**. 

By following these user journeys, you can simulate real-world usage and verify that the backend orchestration, AI agents, and access controls are functioning correctly.

---

## Prerequisites for Testing
Ensure the backend is running locally (`uvicorn app.main:app --reload`) and that you have seeded the database (run `seed_roles.py`, `setup_admin.py`, and `create_departments.py`). 
All testing can be done via the interactive API docs at `http://127.0.0.1:8000/docs` or via tools like Postman / cURL.

**To Test Email Notifications:** 
You must configure your `.env` file with real SMTP credentials (e.g., Gmail App Password) for the background agents to send dispatch emails successfully.
```env
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
SENDER_EMAIL="your_real_email@gmail.com"
SENDER_PASSWORD="your_app_password"
```

---

## Journey 1: The Citizen (Submitting a Grievance)

**Objective**: Verify that a regular citizen can create an account, submit a complaint with media, and that the AI background agents successfully process the ticket.

### 1. Register a Citizen Account
*   **Endpoint:** `POST /api/v1/auth/register`
*   **Payload:**
    ```json
    {
      "email": "test.citizen@example.com",
      "password": "password123"
    }
    ```
*   **Expected:** `200 OK` with user details. 

### 2. Login as the Citizen
*   **Endpoint:** `POST /api/v1/auth/login` (or use the Authorize button in Swagger)
*   **Payload (Form Data):** `username=test.citizen@example.com` & `password=password123`
*   **Expected:** Returns an `access_token`. 

### 3. Submit a Case (Grievance)
*   **Endpoint:** `POST /api/v1/cases/` (Ensure you are authorized with the citizen's token)
*   **Payload:**
    ```json
    {
      "title": "Massive pothole causing accidents",
      "description": "There is a 3-foot wide pothole right in the middle of the intersection.",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "ward": "Ward 5"
    }
    ```
*   **Expected:** Returns `200 OK` with the created case. **Note the `id` of this case** for the next steps. The status should initially be `pending`.

### 4. Verify AI Agent Processing
*   *Background Process:* The moment the case is submitted, the system's background AI agents (Text Agent, Criticality Agent) are triggered.
*   **Endpoint:** `GET /api/v1/cases/{case_id}` (Using the ID from Step 3)
*   **Expected:** Wait 5-10 seconds and fetch the case again. You should observe that:
    1.  The `priority` score has been automatically calculated (e.g., > 70 due to "accidents" keyword).
    2.  The case has been routed to a specific department (e.g., "Roads").

---

## Journey 2: The Department Official (Resolving a Grievance)

**Objective**: Verify that department officials can only access cases assigned to their department, and that they can progress a case to completion.

### 1. Login as an Official
*(Assuming `create_departments.py` was run, default officials exist)*
*   **Endpoint:** `POST /api/v1/auth/login`
*   **Payload (Form Data):** `username=roads_dept@city.com` & `password=password123`
*   **Expected:** Returns an `access_token` for the official.

### 2. View Department Dashboard
*   **Endpoint:** `GET /api/v1/cases/`
*   **Expected:** The official should **only** see cases assigned to the "Roads" department. They should see the case the Citizen created in Journey 1.

### 3. Update Case Status (Start Work)
*   **Endpoint:** `PATCH /api/v1/cases/{case_id}/status`
*   **Payload:** `"processing"` (Note: passing the string directly or as `{ "status": "processing" }` depending on your schema)
*   **Expected:** Returns `200 OK`. The case status is now `processing`.

### 4. Close Case (Verification)
*   **Endpoint:** `PATCH /api/v1/cases/{case_id}/status`
*   **Payload:** `"completed"`
*   **Expected:** Returns `200 OK`. The case is closed, and the system records the `closed_at` timestamp. *(Note: If you have strict business rules, it might require an 'after' photo upload before allowing closure).*

---

## Journey 3: The Super Admin (Audit & Oversight)

**Objective**: Verify that admins have full visibility and can audit system actions.

### 1. Login as Super Admin
*   **Endpoint:** `POST /api/v1/auth/login`
*   **Payload (Form Data):** `username=admin@city.com` & `password=admin123`
*   **Expected:** Returns an `access_token` for the admin.

### 2. View All Cases system-wide
*   **Endpoint:** `GET /api/v1/cases/`
*   **Expected:** The admin sees **all** cases across **all** departments.

### 3. Add a New Department Worker
The system uses dynamic email routing. To add a new official so they receive dispatch emails, the Admin simply creates them via the API:
*   **Endpoint:** `POST /api/v1/admin/users`
*   **Payload:**
    ```json
    {
      "email": "new.worker@city.com",
      "password": "securepassword123",
      "department_name": "Sanitation"
    }
    ```
*   **Expected:** Returns `200 OK`. The next time a case is routed to "Sanitation", this new user will automatically receive an email notification.

### 4. Verify Audit Logs & Blockchain Ledgers
*(If implemented as endpoints or accessible via DB)*
*   **Verification:** Ensure that the actions taken by the citizen (creating the case) and the official (changing status) were correctly recorded in the `audit_logs` and `blockchain_ledgers` tables in the database.
