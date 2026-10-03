"""Create service resources, referral lifecycles, outcomes, and follow-up policies."""

from sqlalchemy import text

import app.db.models  # noqa: F401
from alembic import op
from app.db.base import Base

revision = "0005_resources_referrals"
down_revision = "0004_assessment_evidence"
branch_labels = None
depends_on = None

TABLES = (
    "service_resources",
    "resource_verifications",
    "referrals",
    "referral_events",
    "support_outcomes",
    "follow_up_policies",
    "contact_attempt_policies",
    "follow_ups",
    "contact_attempts",
)


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in TABLES:
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=False)
    for table_name in ("referral_events", "resource_verifications", "support_outcomes"):
        op.execute(
            text(f"""
            CREATE TRIGGER {table_name}_append_only
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update();
        """)
        )


def downgrade() -> None:
    for table_name in reversed(TABLES):
        op.execute(text(f"DROP TRIGGER IF EXISTS {table_name}_append_only ON {table_name}"))
        Base.metadata.tables[table_name].drop(bind=op.get_bind(), checkfirst=False)
