"""Create reference and policy catalogs."""

from sqlalchemy import text

import app.db.models  # noqa: F401
from alembic import op
from app.db.base import Base

revision = "0001_reference_governance"
down_revision = None
branch_labels = None
depends_on = None

TABLES = (
    "jurisdictions",
    "organizations",
    "policy_versions",
    "processing_authority_types",
    "processing_purposes",
)


def upgrade() -> None:
    op.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    bind = op.get_bind()
    for table_name in TABLES:
        Base.metadata.tables[table_name].create(bind=bind, checkfirst=False)


def downgrade() -> None:
    bind = op.get_bind()
    for table_name in reversed(TABLES):
        Base.metadata.tables[table_name].drop(bind=bind, checkfirst=False)
