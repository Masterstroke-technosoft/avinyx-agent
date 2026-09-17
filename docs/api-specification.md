# API Specification

All APIs adhere to RESTful conventions, prefixed with `/api/v1`.

## 1. System Health
*   `GET /api/v1/health`
    *   **Description**: Checks application status and database connectivity.
    *   **Auth Required**: No.

## 2. Authentication
*   `POST /api/v1/auth/register` - Register a new user.
*   `POST /api/v1/auth/login` - Obtain JWT access/refresh tokens.
*   `POST /api/v1/auth/refresh` - Refresh an expired access token.
*   `POST /api/v1/auth/logout` - Invalidate current tokens.
*   `GET /api/v1/auth/me` - Retrieve current user profile.

## 3. Role-Based Access Control (RBAC)
*   `GET /api/v1/roles` - List roles.
*   `POST /api/v1/roles` - Create a role.
*   `POST /api/v1/roles/{id}/permissions` - Assign permissions to a role.

## 4. Case Management (Ingestion & Workflow)
*   `POST /api/v1/cases`
    *   **Description**: Submit a new civic grievance (with text/media).
*   `GET /api/v1/cases`
    *   **Description**: List cases with filtering (by status, ward, citizen).
*   `GET /api/v1/cases/{id}`
    *   **Description**: Retrieve case details.
*   `PATCH /api/v1/cases/{id}/status`
    *   **Description**: Update case status (e.g., dispatch, resolve).

## 5. Field Operations & Closure
*   `POST /api/v1/cases/{id}/verification`
    *   **Description**: Upload before/after photos and GPS coordinates.
*   `POST /api/v1/cases/{id}/close`
    *   **Description**: Trigger the Closure Validation Agent.

## 6. Agent Webhooks (Internal/Async)
*   `POST /api/v1/agents/callback`
    *   **Description**: Endpoint for agents to report processing results (e.g., translation done, vision check complete).
