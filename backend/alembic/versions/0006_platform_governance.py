"""Create PostgreSQL job queue, integration boundary, audit, and deletion tracking."""

from sqlalchemy import text

import app.db.models  # noqa: F401
from alembic import op
from app.db.base import Base

revision = "0006_platform_governance"
down_revision = "0005_resources_referrals"
branch_labels = None
depends_on = None

TABLES = ("async_jobs", "integration_events", "audit_events", "deletion_requests")


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in TABLES:
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=False)
    op.execute(
        text("""
        CREATE TRIGGER audit_events_append_only
        BEFORE UPDATE ON audit_events
        FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update();
    """)
    )


def downgrade() -> None:
    bind = op.get_bind()
    op.execute(text("DROP TRIGGER IF EXISTS audit_events_append_only ON audit_events"))
    for table_name in reversed(TABLES):
        Base.metadata.tables[table_name].drop(bind=bind, checkfirst=False)
