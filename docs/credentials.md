# System & Test Credentials

This document outlines the default passwords and credentials used for local development, testing, and initial system setup. 

> [!WARNING]
> These credentials are for **development and testing environments only**. They must be changed and securely managed (e.g., using environment variables or a secrets manager) before deploying to production.

## 1. Application Users

### Super Admin
The default super admin account is created by running `setup_admin.py`.
*   **Email (Username):** `admin@city.com`
*   **Password:** `admin123`

### Department Officials
When running `create_departments.py` to seed department data, default official accounts are created for each department.
*   **Email format:** (Varies by department, e.g., `water_dept@city.com`)
*   **Default Password:** `password123`

### Citizen / Test Users
In the various test scripts (e.g., `test_full_complaint.py`, `test_phase6.py`), dummy citizen accounts are registered on the fly.
*   **Standard Test Password:** `password123`

---

## 2. Infrastructure & Database

### PostgreSQL (Docker)
When running the local database via `docker-compose.yml`, the default PostgreSQL credentials are:
*   **User:** `postgres`
*   **Password:** `civic_password`
*   **Database:** `civic_db`
*   **Port:** `5432`

> [!TIP]
> To modify the database credentials, update the `.env` file and the corresponding environment variables in your `docker-compose.yml`.
