<<<<<<< HEAD
# Immutable Audit Logging and Compliance System for a Healthcare Platform

Fourth year computer science project. An audit logging system for a company that supports elderly patients and their caregivers. Because the data is sensitive, every access and change to a patient record must be recorded in a log that cannot be altered or deleted after the fact, and that can be independently verified.

## What Sprint 1 delivers

Sprint 1 is data preparation and development environment setup, not features. What exists at the end of this sprint:

- A FastAPI backend with a real, working immutable audit log: create, list, and a chain verification endpoint.
- Tamper resistance at two independent layers: a SHA-256 hash chain in the application, and a Postgres trigger that rejects any UPDATE or DELETE on the audit_logs table outright, even from a database superuser bypassing the API.
- A React and TypeScript frontend that renders live audit records and the chain integrity status from the real API.
- Alembic migrations that build the schema from nothing.
- A seed script producing realistic sample users and audit events.
- Unit tests for the hash chain logic, including a test that proves tampering is detected.
- Docker Compose for one command local setup, plus a Makefile for common tasks.
- Pre-commit hooks and a GitHub Actions CI workflow that lints and tests both sides on every push.

## Architecture

```
frontend (React + TypeScript + Vite)
        |
        v  REST over HTTP
backend (FastAPI, Python)
        |
        v  SQLAlchemy / psycopg2
PostgreSQL  --  audit_logs table protected by an append-only trigger
```

Two layers of protection on the audit trail, on purpose:

1. Application layer: `app/services/audit_service.py` only exposes create and read functions for audit records. There is no update or delete function anywhere in the codebase, and each record's `record_hash` chains to the previous record's hash, so altering historical data breaks every hash after it.
2. Database layer: Alembic migration `0002_audit_log_immutability_trigger.py` installs a Postgres trigger that raises an exception on any UPDATE or DELETE against `audit_logs`, regardless of which tool or role issues the SQL. This is the control an external auditor would actually check for, since it holds even if the application layer is bypassed entirely.

## Running it locally

### Option A: Docker Compose (recommended once your machine can reach Docker Hub)

```
cd audit-log-system
cp backend/.env.example backend/.env
docker compose up --build
```

This starts Postgres, the FastAPI backend (with migrations applied automatically on start), the React frontend, and Adminer for inspecting the database at `http://localhost:8080`.

- Backend: http://localhost:8000 (docs at http://localhost:8000/docs)
- Frontend: http://localhost:5173
- Adminer: http://localhost:8080

Note: in the sandboxed environment this project was built in, outbound access to Docker Hub was blocked by organization policy, so the full stack was instead verified against a locally installed Postgres 16 server and the backend and frontend running directly (see Option B). The docker-compose.yml file itself is complete and was reviewed line by line; it should work as is on a machine with normal internet access, and is worth confirming once on your own laptop before the next check-in.

### Option B: Running services directly (what was used to verify Sprint 1 here)

Backend:

```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # then point DATABASE_URL at your local Postgres
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

Frontend:

```
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Verifying the immutability guarantee yourself

With the backend running against Postgres:

```
curl http://localhost:8000/api/v1/audit-logs/verify
```

Then try to tamper with a row directly in the database, bypassing the API entirely:

```
psql -d audit_log_db -c "UPDATE audit_logs SET action='HACKED' WHERE sequence=1;"
```

This should fail with an error from the `audit_logs_no_update` trigger. That failure, not a success, is the correct and expected result, and is what was confirmed while building this sprint.

## Running tests and linters

```
cd backend
source .venv/bin/activate
pytest -q
ruff check app tests
black --check app tests

cd ../frontend
npm run lint
npm run build
```

Or from the project root: `make test`, `make lint`.

## Project layout

```
audit-log-system/
  backend/
    app/
      core/       settings, security (password hashing, JWT)
      db/         SQLAlchemy session, seed script
      models/     ORM models (User, AuditLog)
      schemas/    Pydantic request/response shapes
      api/v1/     FastAPI routers
      services/   business logic (hash chaining lives here)
    alembic/      database migrations
    tests/        pytest unit tests
  frontend/
    src/
      api/        API client
      pages/       screens
      types/       shared TypeScript types
  docs/
    CONTRIBUTING.md   branch strategy and commit conventions
    sprints/          one file per sprint, tracked deliverables
  docker-compose.yml
  Makefile
  .github/workflows/ci.yml
  .pre-commit-config.yaml
```

## Compliance notes

The system deals with elderly patients' and caregivers' data, which is sensitive. Design decisions made with that in mind so far: role is tracked on every audit event (`actor_role`), the audit table itself cannot be altered after the fact even by an administrator, and passwords are hashed with bcrypt, never stored or logged in plain text. Role-based access control on the API itself (so only authorized roles can read or write specific resources) is scoped for a later sprint; Sprint 1 lays the schema and the User model it will build on.
=======
# AuditLoggingSystem
An immutable audit logging system for a healthcare facility that ensures audit records are tamper-evident, traceable, and integrity-verifiable using hash chaining, PostgreSQL, Redis Streams and anomaly detection.
>>>>>>> 72cf3f78af24edaee3164adffc57bcfa17d8735a
