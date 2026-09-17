# How to Use the Civic System API

This guide will walk you through the end-to-end process of setting up, seeding data, and actually using the Civic Case Management System.

---

## Step 1: Initial Setup & Database
Before using the API, you must ensure the database is running and the tables are created.

1. **Start the PostgreSQL database** (using Docker):
   ```bash
   docker-compose up -d
   ```
2. **Apply Database Migrations** (creates all necessary tables):
   ```bash
   alembic upgrade head
   ```

---

## Step 2: Seed the System with Initial Data
The system needs roles, an admin user, and departments to function correctly. We provide python scripts to set these up automatically.

Run these scripts in order from your terminal:

1. **Seed Roles & Permissions**:
   ```bash
   python seed_roles.py
   ```
2. **Create the Super Admin Account**:
   ```bash
   python setup_admin.py
   ```
   *(Creates login: `admin@city.com` / `admin123`)*
3. **Create Departments & Officials**:
   ```bash
   python create_departments.py
   ```
   *(Creates departments like Water, Roads, Electricity, and their default officials).*

---

## Step 3: Start the Server
Now that the database is populated, start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
The API is now running at `http://127.0.0.1:8000`.

---

## Step 4: Interacting with the API
The easiest way to interact with the API is through the built-in Swagger UI.
👉 **Open your browser and navigate to: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Scenario A: Citizen Submitting a Complaint
1. **Register a Citizen**: Scroll down to `POST /api/v1/auth/register`. Click "Try it out", enter an email and password, and Execute.
2. **Login**: Go to the top right of the page and click the green **"Authorize"** button. Enter the email and password you just created.
3. **Create a Case**: Scroll to `POST /api/v1/cases/`. Click "Try it out".
   *   Enter a title (e.g., "Huge Pothole on Main St").
   *   Enter a description (e.g., "The road is caving in").
   *   Enter latitude/longitude.
   *   Execute. 
4. **Agent Processing**: In the background, the AI agents will automatically analyze the text, calculate a priority score, and assign it to the correct department (e.g., Roads Department).

### Scenario B: Admin / Official Reviewing Cases
1. **Login as Admin**: Click the green **"Authorize"** button, click "Logout" if you are logged in as a citizen, and enter the Admin credentials:
   *   Username: `admin@city.com`
   *   Password: `admin123`
2. **View Cases**: Scroll to `GET /api/v1/cases/`. Click "Try it out" and Execute. You will see all cases in the system, along with the AI-generated priority scores and assigned departments.
3. **Update Case**: Use `PATCH /api/v1/cases/{case_id}/status` to change the case status to `processing` or `completed` once work is done.

---

## Step 5: Testing Automated Scenarios (Optional)
If you want to see the system run automatically without clicking through the Swagger UI, we have built several test scripts that simulate user behavior. 

Open a new terminal window and run:
```bash
pytest test_full_complaint.py -v -s
```
*(This script will automatically create a user, log them in, submit a complaint, trigger the background AI agents, and wait for the final result!)*
