"""enforce audit_logs immutability at the database layer

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-18

This migration is the second layer of tamper-resistance described in
app/services/audit_service.py. Even a database superuser connecting
directly with psql, bypassing the API entirely, cannot UPDATE or
DELETE a row in audit_logs once this trigger is in place: the trigger
function raises an exception before Postgres commits the change.

Rationale for doing this in the database rather than only in the
application layer: the application layer can be bypassed by anyone
with direct DB credentials (a misconfigured admin tool, a
compromised backend, a well-meaning but risky manual fix). A
database-level constraint is the last line of defense and is the
control an external auditor will actually check for.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_audit_log_mutation()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION
                'audit_logs is append-only: % operations are not permitted (row id: %)',
                TG_OP,
                OLD.id;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER audit_logs_no_update
        BEFORE UPDATE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation();
        """
    )
    op.execute(
        """
        CREATE TRIGGER audit_logs_no_delete
        BEFORE DELETE ON audit_logs
        FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS audit_logs_no_delete ON audit_logs;")
    op.execute("DROP TRIGGER IF EXISTS audit_logs_no_update ON audit_logs;")
    op.execute("DROP FUNCTION IF EXISTS prevent_audit_log_mutation();")
