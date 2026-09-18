"""
Hash-chaining logic for the immutable audit log.

Design note for the student (you) reading this later:

Each audit record's `record_hash` is SHA-256 over a canonical string
built from the record's own fields plus the `previous_hash` of the
last record written. That makes the table a hash chain, the same
principle used by blockchains and git commit history: to alter a
past record without detection, an attacker would need to recompute
the hash of that record AND every record after it. Combined with the
database trigger that blocks UPDATE/DELETE outright (see the Alembic
migration), this gives two independent layers of tamper evidence.

`verify_chain` walks the table in insertion order and recomputes each
hash to confirm nothing was altered outside the application (e.g. via
a direct DB console with elevated privileges bypassing the trigger,
or a restored backup that was edited offline).
"""

import hashlib
import json
from typing import Optional

from sqlalchemy import asc
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate


def _canonical_payload(entry: AuditLogCreate, previous_hash: Optional[str]) -> str:
    payload = {
        "actor_id": str(entry.actor_id) if entry.actor_id else None,
        "actor_role": entry.actor_role,
        "action": entry.action,
        "resource_type": entry.resource_type,
        "resource_id": entry.resource_id,
        "metadata_json": entry.metadata_json,
        "ip_address": entry.ip_address,
        "previous_hash": previous_hash,
    }
    return json.dumps(payload, sort_keys=True, default=str)


def _hash_payload(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _get_last_record(db: Session) -> Optional[AuditLog]:
    return db.query(AuditLog).order_by(AuditLog.sequence.desc()).first()


def get_last_hash(db: Session) -> Optional[str]:
    last = _get_last_record(db)
    return last.record_hash if last else None


def create_audit_log(db: Session, entry: AuditLogCreate) -> AuditLog:
    """
    Known limitation, worth calling out explicitly for the audit
    trail's own audit trail: reading the last record and inserting the
    next one are two separate statements, so two concurrent writers
    could both read the same "last" record and race to claim the next
    sequence number. Postgres's unique constraint on `sequence` turns
    that race into a clean IntegrityError on the loser rather than
    silent corruption, but the loser would need to retry. For Sprint 1
    (single-writer API, low write volume) this is an acceptable,
    documented gap; a later sprint should wrap this in
    `SELECT ... FOR UPDATE` on the last row, or a Postgres sequence, to
    close it under concurrent load.
    """
    last_record = _get_last_record(db)
    previous_hash = last_record.record_hash if last_record else None
    next_sequence = (last_record.sequence + 1) if last_record else 1

    payload = _canonical_payload(entry, previous_hash)
    record_hash = _hash_payload(payload)

    db_entry = AuditLog(
        sequence=next_sequence,
        actor_id=entry.actor_id,
        actor_role=entry.actor_role,
        action=entry.action,
        resource_type=entry.resource_type,
        resource_id=entry.resource_id,
        metadata_json=entry.metadata_json,
        ip_address=entry.ip_address,
        previous_hash=previous_hash,
        record_hash=record_hash,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def verify_chain(db: Session) -> tuple[bool, int, Optional[str]]:
    """
    Recompute every record's hash in insertion order and compare it to
    what is stored. Returns (is_valid, records_checked, first_broken_id).
    """
    records = db.query(AuditLog).order_by(asc(AuditLog.sequence)).all()
    expected_previous: Optional[str] = None

    for record in records:
        reconstructed = AuditLogCreate(
            actor_id=record.actor_id,
            actor_role=record.actor_role,
            action=record.action,
            resource_type=record.resource_type,
            resource_id=record.resource_id,
            metadata_json=record.metadata_json,
            ip_address=record.ip_address,
        )
        payload = _canonical_payload(reconstructed, expected_previous)
        recomputed_hash = _hash_payload(payload)

        if record.previous_hash != expected_previous or recomputed_hash != record.record_hash:
            return False, len(records), str(record.id)

        expected_previous = record.record_hash

    return True, len(records), None
