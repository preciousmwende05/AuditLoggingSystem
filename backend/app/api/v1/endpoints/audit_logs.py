from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.audit_log import AuditChainVerification, AuditLogCreate, AuditLogRead
from app.services import audit_service

router = APIRouter()


@router.post("/audit-logs", response_model=AuditLogRead, status_code=201)
def create_audit_log_entry(entry: AuditLogCreate, db: Session = Depends(get_db)):
    """
    Records a single audit event. This is the only write path for the
    audit_logs table; there is deliberately no PUT/PATCH/DELETE here.
    """
    return audit_service.create_audit_log(db, entry)


@router.get("/audit-logs", response_model=List[AuditLogRead])
def list_audit_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    from app.models.audit_log import AuditLog

    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/audit-logs/verify", response_model=AuditChainVerification)
def verify_audit_chain(db: Session = Depends(get_db)):
    """
    Walks the whole chain and confirms no record has been altered.
    Intended for compliance checks / scheduled integrity jobs.
    """
    is_valid, checked, broken_id = audit_service.verify_chain(db)
    return AuditChainVerification(
        is_valid=is_valid,
        records_checked=checked,
        first_broken_record_id=broken_id,
    )
