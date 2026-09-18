"""
Unit tests for the hash-chaining logic in app/services/audit_service.py.

These tests use an in-memory SQLite database so they run fast and
without Docker. Note: the immutability trigger (Alembic migration
0002) is Postgres-specific and is verified separately against a real
Postgres instance (see docker-compose smoke test in the README).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.schemas.audit_log import AuditLogCreate
from app.services import audit_service


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def _sample_entry(action="PATIENT_RECORD_VIEWED", resource_id="patient-1"):
    return AuditLogCreate(
        actor_role="clinician",
        action=action,
        resource_type="patient_record",
        resource_id=resource_id,
        metadata_json={"reason": "routine checkup"},
        ip_address="127.0.0.1",
    )


def test_first_record_has_no_previous_hash(db_session):
    record = audit_service.create_audit_log(db_session, _sample_entry())
    assert record.previous_hash is None
    assert len(record.record_hash) == 64


def test_chain_links_records_in_order(db_session):
    first = audit_service.create_audit_log(db_session, _sample_entry(resource_id="patient-1"))
    second = audit_service.create_audit_log(db_session, _sample_entry(resource_id="patient-2"))

    assert second.previous_hash == first.record_hash


def test_verify_chain_passes_on_untampered_data(db_session):
    for i in range(5):
        audit_service.create_audit_log(db_session, _sample_entry(resource_id=f"patient-{i}"))

    is_valid, checked, broken_id = audit_service.verify_chain(db_session)
    assert is_valid is True
    assert checked == 5
    assert broken_id is None


def test_verify_chain_detects_tampering(db_session):
    from app.models.audit_log import AuditLog

    for i in range(3):
        audit_service.create_audit_log(db_session, _sample_entry(resource_id=f"patient-{i}"))

    # Simulate tampering: directly mutate a historical row's data,
    # bypassing the create_audit_log() API (this is exactly what the
    # Postgres trigger in migration 0002 is designed to block in
    # production; this test proves the hash chain would still catch
    # it even if the trigger were ever removed or bypassed).
    tampered = db_session.query(AuditLog).first()
    tampered.resource_id = "patient-TAMPERED"
    db_session.commit()

    is_valid, _, broken_id = audit_service.verify_chain(db_session)
    assert is_valid is False
    assert broken_id == str(tampered.id)
