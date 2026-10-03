"""Create subjects, cases, interactions, and transcript provenance tables."""

from sqlalchemy import text

import app.db.models  # noqa: F401
from alembic import op
from app.db.base import Base

revision = "0002_casework_interactions"
down_revision = "0001_reference_governance"
branch_labels = None
depends_on = None

TABLES = (
    "subjects",
    "subject_contacts",
    "cases",
    "case_participants",
    "case_status_events",
    "interactions",
    "interaction_events",
    "transcript_segments",
    "translations",
)


def upgrade() -> None:
    bind = op.get_bind()
    for table_name in TABLES:
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=False)
    op.execute(
        text("""
        CREATE OR REPLACE FUNCTION prevent_append_only_update()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'append-only record % cannot be updated', TG_TABLE_NAME;
        END;
        $$;
    """)
    )
    op.execute(
        text("""
        CREATE TRIGGER case_status_events_append_only
        BEFORE UPDATE ON case_status_events
        FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update();
    """)
    )


def downgrade() -> None:
    op.execute(text("DROP TRIGGER IF EXISTS case_status_events_append_only ON case_status_events"))
    bind = op.get_bind()
    for table_name in reversed(TABLES):
        Base.metadata.tables[table_name].drop(bind=bind, checkfirst=False)
    op.execute(text("DROP FUNCTION IF EXISTS prevent_append_only_update()"))
