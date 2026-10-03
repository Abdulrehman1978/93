"""Create casework and transcript provenance tables from an immutable schema snapshot."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0002_casework_interactions"
down_revision = "0001_reference_governance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subjects",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("subject_reference", sa.String(length=80), nullable=False),
        sa.Column(
            "classification",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'IDENTIFIABLE'"),
        ),
        sa.Column("synthetic_marker", sa.String(length=30)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "classification IN ('IDENTIFIABLE','PSEUDONYMIZED','DE_IDENTIFIED','ANONYMIZED_VALIDATED','SYNTHETIC')",
            name="ck_subjects_subjects_classification",
        ),
        sa.CheckConstraint(
            "synthetic_marker IS NULL OR synthetic_marker = 'SYNTHETIC_DEMO'",
            name="ck_subjects_subjects_synthetic_marker",
        ),
        sa.UniqueConstraint("subject_reference", name="uq_subjects_subject_reference"),
    )
    op.create_table(
        "subject_contacts",
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
            sa.ForeignKey("subjects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("contact_value", sa.Text(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("safe_to_use", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "channel IN ('PHONE','EMAIL','POSTAL','OTHER')",
            name="ck_subject_contacts_subject_contacts_channel",
        ),
    )
    op.create_index(
        "ix_subject_contacts_subject_id", "subject_contacts", ["subject_id"], unique=False
    )
    op.create_table(
        "cases",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("public_tracking_id", sa.String(length=32), nullable=False),
        sa.Column(
            "subject_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subjects.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="RESTRICT"),
        ),
        sa.Column(
            "jurisdiction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("jurisdictions.id", ondelete="RESTRICT"),
        ),
        sa.Column("status", sa.String(length=30), nullable=False, server_default=sa.text("'OPEN'")),
        sa.Column(
            "priority", sa.String(length=20), nullable=False, server_default=sa.text("'NORMAL'")
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("version > 0", name="ck_cases_cases_version_positive"),
        sa.CheckConstraint(
            "closed_at IS NULL OR closed_at >= opened_at", name="ck_cases_cases_closed_at"
        ),
        sa.CheckConstraint(
            "status IN ('OPEN','UNDER_REVIEW','REFERRED','ON_HOLD','CLOSED','CANCELLED')",
            name="ck_cases_cases_status",
        ),
        sa.CheckConstraint(
            "priority IN ('LOW','NORMAL','HIGH','URGENT','CRITICAL')",
            name="ck_cases_cases_priority",
        ),
        sa.UniqueConstraint("public_tracking_id", name="uq_cases_public_tracking_id"),
    )
    op.create_index("ix_cases_queue", "cases", ["status", "priority", "created_at"], unique=False)
    op.create_index("ix_cases_jurisdiction_id", "cases", ["jurisdiction_id"], unique=False)
    op.create_index("ix_cases_subject_id", "cases", ["subject_id"], unique=False)
    op.create_table(
        "case_participants",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("participant_reference", sa.String(length=255), nullable=False),
        sa.Column("participant_type", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "participant_type IN ('SUBJECT','OPERATOR','SUPERVISOR','PROVIDER','OTHER')",
            name="ck_case_participants_case_participants_type",
        ),
    )
    op.create_index("ix_case_participants_case_id", "case_participants", ["case_id"], unique=False)
    op.create_table(
        "case_status_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cases.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("previous_status", sa.String(length=30)),
        sa.Column("new_status", sa.String(length=30), nullable=False),
        sa.Column("actor_reference", sa.String(length=255)),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("policy_source", sa.String(length=255)),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "new_status IN ('OPEN','UNDER_REVIEW','REFERRED','ON_HOLD','CLOSED','CANCELLED')",
            name="ck_case_status_events_case_status_events_new_status",
        ),
        sa.CheckConstraint(
            "previous_status IS NULL OR previous_status IN ('OPEN','UNDER_REVIEW','REFERRED','ON_HOLD','CLOSED','CANCELLED')",
            name="ck_case_status_events_case_status_events_previous_status",
        ),
    )
    op.create_index(
        "ix_case_status_events_case_time",
        "case_status_events",
        ["case_id", "occurred_at"],
        unique=False,
    )
    op.create_table(
        "interactions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cases.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'OPEN'")),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("language", sa.String(length=20)),
        sa.Column("external_reference", sa.String(length=255)),
        sa.Column("channel_metadata", postgresql.JSONB()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "channel IN ('VOICE','TEXT','SILENT','IVR','CHATBOT','PORTAL','MOBILE')",
            name="ck_interactions_interactions_channel",
        ),
        sa.CheckConstraint(
            "status IN ('OPEN','COMPLETED','ABANDONED','FAILED')",
            name="ck_interactions_interactions_status",
        ),
        sa.CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name="ck_interactions_interactions_time_range",
        ),
    )
    op.create_index(
        "ix_interactions_case_started", "interactions", ["case_id", "started_at"], unique=False
    )
    op.create_table(
        "interaction_events",
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
            sa.ForeignKey("interactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("source_reference", sa.String(length=255)),
        sa.Column("metadata", postgresql.JSONB()),
    )
    op.create_index(
        "ix_interaction_events_interaction_time",
        "interaction_events",
        ["interaction_id", "occurred_at"],
        unique=False,
    )
    op.create_table(
        "transcript_segments",
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
            sa.ForeignKey("interactions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("start_ms", sa.Integer(), nullable=False),
        sa.Column("end_ms", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("confidence", postgresql.DOUBLE_PRECISION()),
        sa.Column("provider", sa.String(length=100)),
        sa.Column("provider_version", sa.String(length=100)),
        sa.Column("is_final", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="ck_transcript_segments_transcript_segments_confidence",
        ),
        sa.CheckConstraint(
            "sequence >= 0", name="ck_transcript_segments_transcript_segments_sequence_nonnegative"
        ),
        sa.CheckConstraint(
            "start_ms >= 0 AND end_ms >= start_ms",
            name="ck_transcript_segments_transcript_segments_offsets",
        ),
    )
    op.create_index(
        "uq_transcript_segments_interaction_sequence",
        "transcript_segments",
        ["interaction_id", "sequence"],
        unique=True,
    )
    op.create_table(
        "translations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "transcript_segment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("transcript_segments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_language", sa.String(length=20), nullable=False),
        sa.Column("translated_content", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=100)),
        sa.Column("provider_version", sa.String(length=100)),
        sa.Column("confidence", postgresql.DOUBLE_PRECISION()),
        sa.Column(
            "human_review_state",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'NOT_REVIEWED'"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="ck_translations_translations_confidence",
        ),
        sa.CheckConstraint(
            "human_review_state IN ('NOT_REVIEWED','REVIEWED','CORRECTED')",
            name="ck_translations_translations_review_state",
        ),
    )
    op.create_index(
        "ix_translations_source_language",
        "translations",
        ["transcript_segment_id", "target_language"],
        unique=False,
    )
    op.execute(
        sa.text(
            """CREATE OR REPLACE FUNCTION prevent_append_only_update() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'append-only record % cannot be updated', TG_TABLE_NAME; END; $$;"""
        )
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER case_status_events_append_only BEFORE UPDATE ON case_status_events FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DROP TRIGGER IF EXISTS case_status_events_append_only ON case_status_events")
    )
    op.drop_table("translations")
    op.drop_table("transcript_segments")
    op.drop_table("interaction_events")
    op.drop_table("interactions")
    op.drop_table("case_status_events")
    op.drop_table("case_participants")
    op.drop_table("cases")
    op.drop_table("subject_contacts")
    op.drop_table("subjects")
    op.execute(sa.text("DROP FUNCTION IF EXISTS prevent_append_only_update()"))
