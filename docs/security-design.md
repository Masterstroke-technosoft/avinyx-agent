# Security Design

## 1. Authentication
*   **Protocol**: JWT (JSON Web Tokens) with short-lived Access Tokens and secure Refresh Tokens.
*   **Password Storage**: Bcrypt (or Argon2) for strong, salted password hashing.

## 2. Authorization (RBAC)
*   Enforced at the API Dependency level in FastAPI.
*   Roles (e.g., Citizen, Field Worker, Admin) map to specific Permissions.
*   Attempting to access a route without correct permissions yields an immediate HTTP 403 Forbidden.

## 3. Data Protection & Input Validation
*   **Pydantic Models**: Strict input validation for all API routes to prevent injection and unexpected payloads.
*   **SQL Injection**: Mitigated entirely via SQLAlchemy ORM (parameterized queries).
*   **Secrets**: All sensitive data (JWT keys, DB credentials) must be managed via `.env` files or secret managers. Never hardcoded.

## 4. API Security
*   **Rate Limiting**: Apply token bucket or sliding window rate limiting on public endpoints to prevent abuse/DDoS.
*   **CORS**: Strict Cross-Origin Resource Sharing policies.
*   **Headers**: Implement security headers (HSTS, X-Content-Type-Options, etc.).

## 5. Audit & Logging
*   Dedicated `audit_logs` table for administrative and sensitive operations.
*   Logging must *never* include raw passwords, JWTs, or PII in plain text debug streams.
