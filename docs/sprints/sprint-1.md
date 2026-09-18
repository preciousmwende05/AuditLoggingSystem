# Sprint 1: Data Preparation and Development Environment Setup

Applies to all projects regardless of type. Deliverables and status below.

## Deliverables

- [x] A properly set up development environment.
      FastAPI backend with a Python virtual environment and pinned requirements, React and TypeScript frontend with Vite, Postgres 16, Docker Compose for one command startup, a Makefile for common tasks.

- [x] A clean and professionally organized codebase.
      Backend split into core, db, models, schemas, api, services layers. Frontend split into api, pages, types. See the Project layout section of the root README.

- [x] All code maintained using Git version control.
      Repository initialized, `.gitignore` covering secrets and build artifacts, branch strategy and commit convention documented in `docs/CONTRIBUTING.md`, pre-commit hooks configured.

- [x] Relevant data, databases, APIs, files or other resources prepared as applicable.
      Postgres schema built through Alembic migrations (`users`, `audit_logs`), a database level trigger enforcing append-only behavior on `audit_logs`, a seed script producing sample users and audit events, and a working REST API (`/health`, `/audit-logs`, `/audit-logs/verify`).

- [x] Appropriate use of automation for workflow and development management.
      GitHub Actions CI running lint and tests for both backend and frontend on every push and pull request, pre-commit hooks auto-formatting and catching issues before a commit lands, a Makefile standardizing common commands.

## What was actually verified, not just written

- Alembic migrations applied cleanly against a real Postgres 16 database.
- The seed script created 3 users and 3 audit log events successfully.
- The FastAPI server started, connected to Postgres, and served real data.
- `GET /api/v1/audit-logs/verify` returned `is_valid: true` against real data.
- A direct `UPDATE` and a direct `DELETE` against `audit_logs`, issued straight through `psql` (bypassing the API entirely), were both rejected by the database trigger.
- The React frontend, run against the live backend, rendered the audit log table and the chain integrity status correctly (confirmed with a headless browser screenshot).
- The backend unit test suite (hash chain creation, chain verification, tamper detection) passes: 4/4.
- Backend and frontend lint and type-check cleanly.

## Known limitations, carried forward openly rather than hidden

- `docker-compose.yml` was written and reviewed but could not be pulled and run end to end in the sandbox this was built in, because outbound access to Docker Hub was blocked by that environment's network policy. It should be run once on a machine with normal internet access to confirm the container build itself, separate from the application logic already verified directly against Postgres.
- Sequence assignment in `create_audit_log` has a documented race condition under concurrent writers (two requests both reading the same "last record" at once). Low risk at Sprint 1's single writer scale; flagged in the code and here for a later sprint to close with `SELECT ... FOR UPDATE` or a native Postgres sequence.
- Role-based access control on the API endpoints themselves (as opposed to the `role` column existing on `User`) is not yet implemented. Planned for the sprint that adds authentication.

## Next sprint candidates

- JWT-based login and role-based access control on the API.
- Caregiver and patient record models, beyond the generic `resource_type` / `resource_id` audit fields.
- Pagination and filtering on the audit log list endpoint and dashboard.
- Confirm `docker compose up` end to end on a machine with unrestricted internet access.
