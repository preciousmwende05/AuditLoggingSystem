"""
User and role model.

Roles are kept intentionally simple for Sprint 1 (an enum column) so
role-based access control (RBAC) can be layered on in a later sprint
without a schema rewrite.
"""

import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CLINICIAN = "clinician"
    CAREGIVER = "caregiver"
    AUDITOR = "auditor"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    # values_callable makes SQLAlchemy store/compare the enum's lowercase
    # *values* ("admin") against the Postgres user_role type, rather
    # than its default of the Python member *names* ("ADMIN"). The
    # migration creates the enum type with lowercase labels, so this
    # must match, or every insert fails with an invalid-enum-value error.
    role = Column(
        Enum(
            UserRole, name="user_role", values_callable=lambda enum_cls: [e.value for e in enum_cls]
        ),
        nullable=False,
        default=UserRole.CAREGIVER,
    )
    is_active = Column(String, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
