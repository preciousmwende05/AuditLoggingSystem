"""
Append-only audit log model.

Immutability is enforced at two layers, deliberately:
1. Database layer: a trigger (see alembic migration 0002) rejects any
   UPDATE or DELETE on this table outright, regardless of which
   application or role issues the SQL.
2. Application layer: no service function in this codebase exposes an
   update or delete path for audit records; only create and read.

Tamper evidence is provided by hash chaining: each row stores the
SHA-256 hash of its own canonical content plus the previous row's
hash (`previous_hash`), so altering any historical row breaks the
chain for every row after it, and that break is verifiable without a
separate audit trail of the audit trail.
"""

import uuid

from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.session import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Monotonically increasing chain position, assigned explicitly by
    # audit_service.create_audit_log() (see the comment there for why).
    # created_at is kept for human-readable/reporting purposes, but
    # ordering the hash chain by a timestamp is unsafe: two inserts
    # within the same clock tick can tie, which would make chain order
    # ambiguous. Ordering by `sequence` is always exactly insertion
    # order, which is what the hash chain requires.
    sequence = Column(BigInteger, nullable=False, unique=True, index=True)

    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    actor_role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)  # e.g. "PATIENT_RECORD_VIEWED"
    resource_type = Column(String(100), nullable=False)  # e.g. "patient_record"
    resource_id = Column(String(255), nullable=True)

    # Postgres in prod/dev (via docker-compose) gets real JSONB; SQLite
    # (used only by the fast in-memory unit tests) falls back to JSON.
    metadata_json = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    ip_address = Column(String(45), nullable=True)

    previous_hash = Column(String(64), nullable=True)
    record_hash = Column(String(64), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
