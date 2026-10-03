"""Create assessment dimensions, provenance, evidence pointers, and reviews from an immutable schema snapshot."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0004_assessment_evidence"
down_revision = "0003_privacy_authorization"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assessments",
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
        sa.Column(
            "interaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("interactions.id", ondelete="RESTRICT"),
        ),
        sa.Column(
            "assessment_type",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'TRIAGE'"),
        ),
        sa.Column(
            "status", sa.String(length=25), nullable=False, server_default=sa.text("'ADVISORY'")
        ),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "version_number > 0", name="ck_assessments_assessments_version_positive"
        ),
        sa.CheckConstraint(
            "assessment_type IN ('TRIAGE','RECALCULATION','HUMAN_REVIEW')",
            name="ck_assessments_assessments_type",
        ),
        sa.CheckConstraint(
            "status IN ('ADVISORY','UNDER_REVIEW','FINALIZED','DISMISSED')",
            name="ck_assessments_assessments_status",
        ),
    )
    op.create_index(
        "ix_assessments_case_created", "assessments", ["case_id", "created_at"], unique=False
    )
    op.create_index(
        "ix_assessments_interaction_id", "assessments", ["interaction_id"], unique=False
    )
    op.create_table(
        "model_runs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("task", sa.String(length=80), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=150), nullable=False),
        sa.Column("model_version", sa.String(length=100), nullable=False),
        sa.Column("prompt_version", sa.String(length=100)),
        sa.Column("input_reference", sa.String(length=500), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("failure_class", sa.String(length=100)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('STARTED','SUCCEEDED','FAILED','CANCELLED')",
            name="ck_model_runs_model_runs_status",
        ),
        sa.CheckConstraint(
            "latency_ms IS NULL OR latency_ms >= 0",
            name="ck_model_runs_model_runs_latency_nonnegative",
        ),
        sa.CheckConstraint(
            "completed_at IS NULL OR completed_at >= started_at",
            name="ck_model_runs_model_runs_time_range",
        ),
    )
    op.create_table(
        "immediate_safety_results",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessments.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("state", sa.String(length=35), nullable=False),
        sa.Column("confidence", postgresql.DOUBLE_PRECISION()),
        sa.Column(
            "policy_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("policy_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "model_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("model_runs.id", ondelete="RESTRICT"),
        ),
        sa.Column("uncertainty", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "state IN ('NO_IMMEDIATE_SIGNAL','REVIEW_RECOMMENDED','ELEVATED','CRITICAL_REVIEW','INSUFFICIENT_INFORMATION')",
            name="ck_immediate_safety_results_immediate_safety_results_state",
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="ck_immediate_safety_results_immediate_safety_results_confidence",
        ),
    )
    op.create_index(
        "ix_immediate_safety_results_assessment_id",
        "immediate_safety_results",
        ["assessment_id"],
        unique=False,
    )
    op.create_table(
        "svi_results",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessments.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("band", sa.String(length=20)),
        sa.Column("numeric_score", postgresql.DOUBLE_PRECISION()),
        sa.Column(
            "policy_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("policy_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "model_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("model_runs.id", ondelete="RESTRICT"),
        ),
        sa.Column("uncertainty", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "band IS NULL OR band IN ('LOW','MODERATE','HIGH','CRITICAL')",
            name="ck_svi_results_svi_results_band",
        ),
        sa.CheckConstraint(
            "numeric_score IS NULL OR numeric_score >= 0",
            name="ck_svi_results_svi_results_numeric_score",
        ),
    )
    op.create_index("ix_svi_results_assessment_id", "svi_results", ["assessment_id"], unique=False)
    op.create_table(
        "incident_urgency_results",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessments.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("confidence", postgresql.DOUBLE_PRECISION()),
        sa.Column(
            "policy_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("policy_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "model_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("model_runs.id", ondelete="RESTRICT"),
        ),
        sa.Column("uncertainty", sa.Text()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "level IN ('ROUTINE','PRIORITY','URGENT','CRITICAL')",
            name="ck_incident_urgency_results_incident_urgency_results_level",
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="ck_incident_urgency_results_incident_urgency_results_confidence",
        ),
    )
    op.create_index(
        "ix_incident_urgency_results_assessment_id",
        "incident_urgency_results",
        ["assessment_id"],
        unique=False,
    )
    op.create_table(
        "assessment_evidence",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessments.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("modality", sa.String(length=30), nullable=False),
        sa.Column("signal_type", sa.String(length=100), nullable=False),
        sa.Column("source_reference", sa.String(length=500), nullable=False),
        sa.Column("source_start", sa.Integer()),
        sa.Column("source_end", sa.Integer()),
        sa.Column("confidence", postgresql.DOUBLE_PRECISION()),
        sa.Column("quality", postgresql.DOUBLE_PRECISION()),
        sa.Column("provider", sa.String(length=100)),
        sa.Column("model_identifier", sa.String(length=150)),
        sa.Column("provenance", postgresql.JSONB()),
        sa.Column("uncertainty", sa.Text()),
        sa.Column(
            "human_review_status",
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
            "human_review_status IN ('NOT_REVIEWED','REVIEWED','DISMISSED')",
            name="ck_assessment_evidence_assessment_evidence_review_status",
        ),
        sa.CheckConstraint(
            "source_end IS NULL OR source_start IS NULL OR source_end >= source_start",
            name="ck_assessment_evidence_assessment_evidence_source_range",
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR confidence BETWEEN 0 AND 1",
            name="ck_assessment_evidence_assessment_evidence_confidence",
        ),
        sa.CheckConstraint(
            "quality IS NULL OR quality BETWEEN 0 AND 1",
            name="ck_assessment_evidence_assessment_evidence_quality",
        ),
        sa.CheckConstraint(
            "source_start IS NULL OR source_start >= 0",
            name="ck_assessment_evidence_assessment_evidence_source_start",
        ),
        sa.CheckConstraint(
            "source_end IS NULL OR source_end >= 0",
            name="ck_assessment_evidence_assessment_evidence_source_end",
        ),
    )
    op.create_index(
        "ix_assessment_evidence_assessment_id",
        "assessment_evidence",
        ["assessment_id"],
        unique=False,
    )
    op.create_table(
        "assessment_reviews",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessments.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("actor_reference", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("previous_output_reference", sa.String(length=500)),
        sa.Column("replacement_reference", sa.String(length=500)),
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
        sa.CheckConstraint(
            "action IN ('ACCEPT','MODIFY','DISMISS','ESCALATE','REQUEST_SUPERVISOR','CORRECT_TRANSCRIPT','CORRECT_FACT','FLAG_AI_ERROR')",
            name="ck_assessment_reviews_assessment_reviews_action",
        ),
    )
    op.create_index(
        "ix_assessment_reviews_assessment_time",
        "assessment_reviews",
        ["assessment_id", "created_at"],
        unique=False,
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER model_runs_append_only BEFORE UPDATE ON model_runs FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER immediate_safety_results_append_only BEFORE UPDATE ON immediate_safety_results FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER svi_results_append_only BEFORE UPDATE ON svi_results FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER incident_urgency_results_append_only BEFORE UPDATE ON incident_urgency_results FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER assessment_evidence_append_only BEFORE UPDATE ON assessment_evidence FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER assessment_reviews_append_only BEFORE UPDATE ON assessment_reviews FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DROP TRIGGER IF EXISTS assessment_reviews_append_only ON assessment_reviews")
    )
    op.execute(
        sa.text("DROP TRIGGER IF EXISTS assessment_evidence_append_only ON assessment_evidence")
    )
    op.execute(
        sa.text(
            "DROP TRIGGER IF EXISTS incident_urgency_results_append_only ON incident_urgency_results"
        )
    )
    op.execute(sa.text("DROP TRIGGER IF EXISTS svi_results_append_only ON svi_results"))
    op.execute(
        sa.text(
            "DROP TRIGGER IF EXISTS immediate_safety_results_append_only ON immediate_safety_results"
        )
    )
    op.execute(sa.text("DROP TRIGGER IF EXISTS model_runs_append_only ON model_runs"))
    op.drop_table("assessment_reviews")
    op.drop_table("assessment_evidence")
    op.drop_table("incident_urgency_results")
    op.drop_table("svi_results")
    op.drop_table("immediate_safety_results")
    op.drop_table("model_runs")
    op.drop_table("assessments")
