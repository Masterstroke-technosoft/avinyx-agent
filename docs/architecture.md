# Architecture Document

## 1. High-Level Architecture
The system operates as an asynchronous, decoupled pipeline.

```text
Client / External System (Web, Mobile, WhatsApp)
        |
        v
     HTTPS/TLS
        |
        v
   API Gateway (Rate Limiting, Routing)
        |
        v
    FastAPI Core Backend
        |
        +-------------------+
        |                   |
        v                   v
 Authentication        Authorization (RBAC)
        |                   |
        +---------+---------+
                  |
                  v
           Business Logic & Orchestrator
                  |
        +---------+---------+---------+
        |                   |         |
        v                   v         v
   PostgreSQL             Redis     Blockchain / External Services
   (State, Relational)   (Queue, Cache)
```

## 2. Core Components
*   **API Gateway**: Handles ingestion, rate limiting, and basic authentication.
*   **Agent Orchestrator (Workflow Engine)**: Manages state machines, evaluates municipal bylaws, and dispatches jobs.
*   **Message Queue (Redis/RabbitMQ)**: Enterprise message queue for async agent communication.
*   **Agent Pools**:
    *   *Text Pool*: Language Understanding, Geo-Mapping, Duplicate Detection, Priority Scoring.
    *   *Vision Pool*: Image/Video classification.
    *   *Critical Pool*: SLA tracking, Emergency Alerts.
    *   *Audit/Closure Pool*: Field verification, validation, and inter-department coordination.
*   **Persistence Layer**: 
    *   Aiven PostgreSQL (Managed Cloud Database for Transactional OLTP).
    *   Object Storage (S3-compatible for Media).
    *   Blockchain Ledger (Audit Trails).

## 3. Technology Stack
*   **Backend Framework**: Python + FastAPI
*   **Database**: Aiven PostgreSQL (via SQLAlchemy & Alembic)
*   **Caching/Queues**: Redis
*   **Containerization**: Docker & Docker Compose
*   **Testing**: Pytest
