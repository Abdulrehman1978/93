"""Add the encrypted, append-only citizen intake entry table."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0012_citizen_intake"
down_revision = "0011_packet06r2_hardening"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "citizen_intake_entries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "interaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("interactions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("entry_type", sa.String(length=20), nullable=False),
        sa.Column("question_code", sa.String(length=60), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("client_submission_id", sa.String(length=80), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("sequence > 0", name="ck_citizen_intake_entries_sequence_positive"),
        sa.CheckConstraint(
            "entry_type IN ('NARRATIVE','STRUCTURED_ANSWER')",
            name="ck_citizen_intake_entries_entry_type",
        ),
    )
    op.create_index(
        "ix_citizen_intake_entries_interaction_sequence",
        "citizen_intake_entries",
        ["interaction_id", "sequence"],
    )
    op.create_index(
        "ix_citizen_intake_entries_interaction_created",
        "citizen_intake_entries",
        ["interaction_id", "created_at"],
    )
    op.create_index(
        "uq_citizen_intake_entries_submission_sequence",
        "citizen_intake_entries",
        ["interaction_id", "client_submission_id", "sequence"],
        unique=True,
    )
    op.execute(
        sa.text(
            """
            CREATE TRIGGER citizen_intake_entries_append_only
            BEFORE UPDATE OR DELETE ON citizen_intake_entries
            FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DROP TRIGGER IF EXISTS citizen_intake_entries_append_only ON citizen_intake_entries"
        )
    )
    op.drop_index(
        "uq_citizen_intake_entries_submission_sequence", table_name="citizen_intake_entries"
    )
    op.drop_index(
        "ix_citizen_intake_entries_interaction_created", table_name="citizen_intake_entries"
    )
    op.drop_index(
        "ix_citizen_intake_entries_interaction_sequence", table_name="citizen_intake_entries"
    )
    op.drop_table("citizen_intake_entries")
