# Database Design

## 1. Core Principles
*   **Database**: Aiven PostgreSQL (Managed Cloud Database)
*   **ORM**: SQLAlchemy
*   **Migrations**: Alembic
*   **Design**: Relational, 3NF where applicable, soft deletion via `deleted_at` timestamps.

## 2. Core Entities

### User Management
*   **users**: `id`, `email`, `hashed_password`, `is_active`, `created_at`, `updated_at`.
*   **roles**: `id`, `name`, `description`.
*   **permissions**: `id`, `name`, `description`.
*   **user_roles** (Join Table): `user_id`, `role_id`.
*   **role_permissions** (Join Table): `role_id`, `permission_id`.

### Case Management
*   **cases (tickets)**: `id`, `citizen_id` (fk), `title`, `description`, `status` (enum), `priority` (integer/score), `latitude`, `longitude`, `ward`, `created_at`, `updated_at`, `closed_at`.
*   **media_attachments**: `id`, `case_id` (fk), `file_url`, `media_type` (image/video), `stage` (before/after).

### Orchestration & Agents
*   **agent_tasks**: `id`, `case_id` (fk), `agent_type` (enum), `status` (pending/processing/completed/failed), `result_payload` (JSONB).

### System & Audit
*   **audit_logs**: `id`, `user_id` (fk), `action`, `resource_type`, `resource_id`, `ip_address`, `timestamp`.
*   **blockchain_ledgers**: `id`, `case_id` (fk), `transaction_hash`, `timestamp`.
