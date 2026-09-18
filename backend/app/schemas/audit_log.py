import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class AuditLogCreate(BaseModel):
    actor_id: Optional[uuid.UUID] = None
    actor_role: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    metadata_json: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sequence: int
    actor_id: Optional[uuid.UUID]
    actor_role: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    metadata_json: Optional[dict[str, Any]]
    ip_address: Optional[str]
    previous_hash: Optional[str]
    record_hash: str
    created_at: datetime


class AuditChainVerification(BaseModel):
    is_valid: bool
    records_checked: int
    first_broken_record_id: Optional[uuid.UUID] = None
