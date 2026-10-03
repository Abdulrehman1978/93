"""Create consent and lawful-processing ledgers from an immutable schema snapshot."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0003_privacy_authorization"
down_revision = "0002_casework_interactions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consent_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "subject_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subjects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="RESTRICT")
        ),
        sa.Column(
            "purpose_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("processing_purposes.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("choice", sa.String(length=30), nullable=False),
        sa.Column(
            "policy_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("policy_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(length=30), nullable=False),
        sa.Column("actor_reference", sa.String(length=255)),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "previous_event_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("consent_events.id", ondelete="RESTRICT"),
        ),
        sa.Column("reason", sa.Text()),
        sa.CheckConstraint(
            "channel IN ('PORTAL','VOICE','TEXT','IVR','OPERATOR','SYSTEM')",
            name="ck_consent_events_consent_events_channel",
        ),
        sa.CheckConstraint(
            "choice IN ('GRANTED','DECLINED','REVOKED','EXPIRED','SUPERSEDED')",
            name="ck_consent_events_consent_events_choice",
        ),
    )
    op.create_index(
        "ix_consent_events_subject_purpose_time",
        "consent_events",
        ["subject_id", "purpose_id", "occurred_at"],
        unique=False,
    )
    op.create_table(
        "processing_authorizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="RESTRICT")
        ),
        sa.Column(
            "interaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("interactions.id", ondelete="RESTRICT"),
        ),
        sa.Column(
            "processing_purpose_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("processing_purposes.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "authority_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("processing_authority_types.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "consent_event_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("consent_events.id", ondelete="RESTRICT"),
        ),
        sa.Column("actor_reference", sa.String(length=255)),
        sa.Column("authorization_reason", sa.Text(), nullable=False),
        sa.Column(
            "policy_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("policy_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "expires_at IS NULL OR expires_at >= created_at",
            name="ck_processing_authorizations_processing_authorizations_expiry",
        ),
        sa.CheckConstraint(
            "case_id IS NOT NULL OR interaction_id IS NOT NULL",
            name="ck_processing_authorizations_processing_authorizations_scope_required",
        ),
    )
    op.create_index(
        "ix_processing_authorizations_case_id",
        "processing_authorizations",
        ["case_id"],
        unique=False,
    )
    op.create_index(
        "ix_processing_authorizations_interaction_id",
        "processing_authorizations",
        ["interaction_id"],
        unique=False,
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER consent_events_append_only BEFORE UPDATE ON consent_events FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TRIGGER IF EXISTS consent_events_append_only ON consent_events"))
    op.drop_table("processing_authorizations")
    op.drop_table("consent_events")
