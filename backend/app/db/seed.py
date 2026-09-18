"""
Sprint 1 seed script.

Populates a small, realistic set of users and audit log events so the
frontend dashboard and the /audit-logs/verify endpoint have something
to show without needing a real caregiver-facing feature yet.

Run inside the backend container or venv with:
    python -m app.db.seed
"""

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.schemas.audit_log import AuditLogCreate
from app.services import audit_service


def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already has users; skipping seed to avoid duplicates.")
            return

        admin = User(
            full_name="Amina Njoroge",
            email="admin@example.com",
            hashed_password=hash_password("ChangeMe123!"),
            role=UserRole.ADMIN,
        )
        clinician = User(
            full_name="Dr. James Otieno",
            email="clinician@example.com",
            hashed_password=hash_password("ChangeMe123!"),
            role=UserRole.CLINICIAN,
        )
        caregiver = User(
            full_name="Grace Wambui",
            email="caregiver@example.com",
            hashed_password=hash_password("ChangeMe123!"),
            role=UserRole.CAREGIVER,
        )
        db.add_all([admin, clinician, caregiver])
        db.commit()
        db.refresh(clinician)
        db.refresh(caregiver)

        sample_events = [
            AuditLogCreate(
                actor_id=clinician.id,
                actor_role="clinician",
                action="PATIENT_RECORD_VIEWED",
                resource_type="patient_record",
                resource_id="patient-001",
                metadata_json={"reason": "routine checkup"},
                ip_address="10.0.0.5",
            ),
            AuditLogCreate(
                actor_id=caregiver.id,
                actor_role="caregiver",
                action="MEDICATION_LOG_UPDATED",
                resource_type="medication_log",
                resource_id="patient-001",
                metadata_json={"medication": "metformin", "dose_confirmed": True},
                ip_address="10.0.0.9",
            ),
            AuditLogCreate(
                actor_id=admin.id,
                actor_role="admin",
                action="USER_ROLE_CHANGED",
                resource_type="user",
                resource_id=str(caregiver.id),
                metadata_json={"old_role": "caregiver", "new_role": "caregiver"},
                ip_address="10.0.0.1",
            ),
        ]
        for event in sample_events:
            audit_service.create_audit_log(db, event)

        print("Seed complete: 3 users, 3 audit log events.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
