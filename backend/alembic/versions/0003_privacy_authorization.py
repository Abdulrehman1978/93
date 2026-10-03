"""Create separate consent and lawful-processing authorization ledgers."""

from sqlalchemy import text

import app.db.models  # noqa: F401
from alembic import op
from app.db.base import Base

revision = "0003_privacy_authorization"
down_revision = "0002_casework_interactions"
branch_labels = None
depends_on = None

TABLES = ("consent_events", "processing_authorizations")


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in TABLES:
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=False)
    op.execute(
        text("""
        CREATE TRIGGER consent_events_append_only
        BEFORE UPDATE ON consent_events
        FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update();
    """)
    )


def downgrade() -> None:
    op.execute(text("DROP TRIGGER IF EXISTS consent_events_append_only ON consent_events"))
    bind = op.get_bind()
    for table_name in reversed(TABLES):
        Base.metadata.tables[table_name].drop(bind=bind, checkfirst=False)
