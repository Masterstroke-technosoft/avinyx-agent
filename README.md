# Civic Case Management System API

A production-ready, autonomous, multi-agent civic case management backend platform. It provides a RESTful API for grievance ingestion, automated case triage using AI agents, and a blockchain-backed ledger for immutable audit trails.

## Current Project Status
**Milestones Completed:** Phase 1 to Phase 11 (API Backend Completed) ✅

The core backend API is fully implemented and tested. It handles authentication, role-based access control, departmental case assignment, and autonomous task queuing.
*(Note: Mobile, web, and WhatsApp frontend interfaces are separate future implementations and not part of this repository).*

## Key Features
*   **REST API Ingestion:** Fully documented API endpoints for submitting complaints, uploading media, and checking case statuses.
*   **Authentication & RBAC:** Secure JWT-based access for Citizens, Department Officials, and Super Admins.
*   **Agent Orchestration:** Autonomous background agents (via tasks/queues) handle:
    *   **Text & Intent Analysis:** Evaluates case descriptions, scores priority, and assigns the correct department.
    *   **Vision Processing:** Analyzes uploaded 'before/after' media.
*   **Blockchain Ledger:** Critical milestones and transactions are securely hashed for transparency and tamper-proofing.
*   **Audit Logging:** Comprehensive tracking of all actions taken by users or agents.

## Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Python 3.10+ (for local development outside docker)

### Running the System
1. **Clone the repository.**
2. **Setup environment variables:**
   ```bash
   cp .env.example .env
   ```
3. **Start the database via Docker:**
   ```bash
   docker-compose up -d
   ```
4. **Run migrations (if applicable):**
   ```bash
   alembic upgrade head
   ```
5. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Documentation & Credentials
*   **API Documentation:** Once the server is running, visit `http://127.0.0.1:8000/docs` to interact with the API Swagger UI.
*   **Default Credentials:** Check `docs/credentials.md` for information on default test and admin accounts.
*   **Architecture Details:** Explore the `docs/` folder for in-depth architecture, database, and security design specifications.

## Testing
The project includes a comprehensive suite of Pytest scripts covering different workflows.
```bash
pytest test_full_complaint.py
```
