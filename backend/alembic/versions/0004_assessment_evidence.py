"""Create assessment dimensions, provenance, evidence pointers, and reviews."""

from sqlalchemy import text

import app.db.models  # noqa: F401
from alembic import op
from app.db.base import Base

revision = "0004_assessment_evidence"
down_revision = "0003_privacy_authorization"
branch_labels = None
depends_on = None

TABLES = (
    "assessments",
    "model_runs",
    "immediate_safety_results",
    "svi_results",
    "incident_urgency_results",
    "assessment_evidence",
    "assessment_reviews",
)


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in TABLES:
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=False)
    for table_name in TABLES[1:]:
        op.execute(
            text(f"""
            CREATE TRIGGER {table_name}_append_only
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update();
        """)
        )


def downgrade() -> None:
    bind = op.get_bind()
    for table_name in reversed(TABLES):
        op.execute(text(f"DROP TRIGGER IF EXISTS {table_name}_append_only ON {table_name}"))
        Base.metadata.tables[table_name].drop(bind=bind, checkfirst=False)
