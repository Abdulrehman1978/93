"""Create service resources, referral lifecycles, outcomes, and follow-up policies from an immutable schema snapshot."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0005_resources_referrals"
down_revision = "0004_assessment_evidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_resources",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("canonical_identifier", sa.String(length=150), nullable=False),
        sa.Column("service_type", sa.String(length=80), nullable=False),
        sa.Column("provider_name", sa.String(length=255), nullable=False),
        sa.Column(
            "jurisdiction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("jurisdictions.id", ondelete="RESTRICT"),
        ),
        sa.Column("languages", postgresql.ARRAY(sa.String(length=20))),
        sa.Column("contact_channel", sa.String(length=30), nullable=False),
        sa.Column("contact_endpoint", sa.String(length=500), nullable=False),
        sa.Column(
            "availability_status",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'UNKNOWN'"),
        ),
        sa.Column(
            "capacity_status",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'NOT_REPORTED'"),
        ),
        sa.Column("capacity_last_reported_at", sa.DateTime(timezone=True)),
        sa.Column(
            "freshness_status",
            sa.String(length=25),
            nullable=False,
            server_default=sa.text("'UNKNOWN'"),
        ),
        sa.Column(
            "integration_status",
            sa.String(length=25),
            nullable=False,
            server_default=sa.text("'NOT_CONFIGURED'"),
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
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
        sa.CheckConstraint(
            "freshness_status IN ('VERIFIED_CURRENT','STALE','UNKNOWN')",
            name="ck_service_resources_service_resources_freshness_status",
        ),
        sa.UniqueConstraint(
            "canonical_identifier", name="uq_service_resources_canonical_identifier"
        ),
        sa.CheckConstraint(
            "contact_channel IN ('PHONE','EMAIL','WEB','PORTAL','IN_PERSON','OTHER')",
            name="ck_service_resources_service_resources_contact_channel",
        ),
        sa.CheckConstraint(
            "integration_status IN ('NOT_CONFIGURED','SANDBOX','ADAPTER_READY','LIVE','DEGRADED','DISABLED')",
            name="ck_service_resources_service_resources_integration_status",
        ),
        sa.CheckConstraint(
            "availability_status IN ('OPEN','LIMITED','CLOSED','UNKNOWN')",
            name="ck_service_resources_service_resources_availability_status",
        ),
        sa.CheckConstraint(
            "version > 0", name="ck_service_resources_service_resources_version_positive"
        ),
        sa.CheckConstraint(
            "capacity_status IN ('AVAILABLE','LIMITED','FULL','NOT_REPORTED')",
            name="ck_service_resources_service_resources_capacity_status",
        ),
    )
    op.create_index(
        "ix_service_resources_lookup",
        "service_resources",
        ["jurisdiction_id", "service_type", "freshness_status"],
        unique=False,
    )
    op.create_table(
        "resource_verifications",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "service_resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_resources.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "verified_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("verification_method", sa.String(length=40), nullable=False),
        sa.Column("verified_by", sa.String(length=255), nullable=False),
        sa.Column("result", sa.String(length=25), nullable=False),
        sa.Column("source_reference", sa.String(length=500)),
        sa.Column("notes", sa.Text()),
        sa.CheckConstraint(
            "result IN ('VERIFIED_CURRENT','STALE','UNAVAILABLE','UNABLE_TO_VERIFY')",
            name="ck_resource_verifications_resource_verifications_result",
        ),
    )
    op.create_index(
        "ix_resource_verifications_resource_time",
        "resource_verifications",
        ["service_resource_id", "verified_at"],
        unique=False,
    )
    op.create_table(
        "referrals",
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
        sa.Column("service_type", sa.String(length=80), nullable=False),
        sa.Column(
            "service_resource_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("service_resources.id", ondelete="RESTRICT"),
        ),
        sa.Column(
            "processing_authorization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("processing_authorizations.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "consent_event_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("consent_events.id", ondelete="RESTRICT"),
        ),
        sa.Column(
            "status", sa.String(length=30), nullable=False, server_default=sa.text("'RECOMMENDED'")
        ),
        sa.Column(
            "priority", sa.String(length=20), nullable=False, server_default=sa.text("'NORMAL'")
        ),
        sa.Column(
            "policy_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("policy_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("next_action_at", sa.DateTime(timezone=True)),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
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
        sa.CheckConstraint(
            "status IN ('RECOMMENDED','REVIEW_REQUIRED','APPROVED','DECLINED','REFERRED','ACKNOWLEDGED','CONTACT_PENDING','CONTACTED','APPOINTMENT_SCHEDULED','SERVICE_STARTED','FOLLOW_UP_DUE','COMPLETED','UNABLE_TO_CONTACT','ESCALATED','CANCELLED')",
            name="ck_referrals_referrals_status",
        ),
        sa.CheckConstraint(
            "priority IN ('LOW','NORMAL','HIGH','URGENT','CRITICAL')",
            name="ck_referrals_referrals_priority",
        ),
        sa.CheckConstraint("version > 0", name="ck_referrals_referrals_version_positive"),
    )
    op.create_index(
        "ix_referrals_queue", "referrals", ["status", "next_action_at", "priority"], unique=False
    )
    op.create_index("ix_referrals_case_id", "referrals", ["case_id"], unique=False)
    op.create_table(
        "referral_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "referral_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("referrals.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("previous_status", sa.String(length=30)),
        sa.Column("new_status", sa.String(length=30), nullable=False),
        sa.Column("actor_reference", sa.String(length=255)),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "new_status IN ('RECOMMENDED','REVIEW_REQUIRED','APPROVED','DECLINED','REFERRED','ACKNOWLEDGED','CONTACT_PENDING','CONTACTED','APPOINTMENT_SCHEDULED','SERVICE_STARTED','FOLLOW_UP_DUE','COMPLETED','UNABLE_TO_CONTACT','ESCALATED','CANCELLED')",
            name="ck_referral_events_referral_events_new_status",
        ),
        sa.CheckConstraint(
            "previous_status IS NULL OR previous_status IN ('RECOMMENDED','REVIEW_REQUIRED','APPROVED','DECLINED','REFERRED','ACKNOWLEDGED','CONTACT_PENDING','CONTACTED','APPOINTMENT_SCHEDULED','SERVICE_STARTED','FOLLOW_UP_DUE','COMPLETED','UNABLE_TO_CONTACT','ESCALATED','CANCELLED')",
            name="ck_referral_events_referral_events_previous_status",
        ),
    )
    op.create_index(
        "ix_referral_events_referral_time",
        "referral_events",
        ["referral_id", "occurred_at"],
        unique=False,
    )
    op.create_table(
        "support_outcomes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "referral_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("referrals.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("outcome_stage", sa.String(length=40), nullable=False),
        sa.Column(
            "evidence_state",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'UNVERIFIED'"),
        ),
        sa.Column("provenance", postgresql.JSONB()),
        sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("verified_by", sa.String(length=255)),
        sa.Column("document_reference", sa.String(length=500)),
        sa.Column("notes_reference", sa.String(length=500)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "evidence_state IN ('UNVERIFIED','PROVIDER_CONFIRMED','CITIZEN_CONFIRMED','DUAL_CONFIRMED','DOCUMENT_CONFIRMED','UNABLE_TO_VERIFY')",
            name="ck_support_outcomes_support_outcomes_evidence_state",
        ),
        sa.CheckConstraint(
            "outcome_stage IN ('RECOMMENDED','REFERRED','ACKNOWLEDGED','CONTACTED','SERVICE_STARTED','FOLLOW_UP_CONFIRMED','COMPLETED')",
            name="ck_support_outcomes_support_outcomes_outcome_stage",
        ),
    )
    op.create_index(
        "ix_support_outcomes_referral_time",
        "support_outcomes",
        ["referral_id", "created_at"],
        unique=False,
    )
    op.create_table(
        "follow_up_policies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "policy_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("policy_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("source_class", sa.String(length=40), nullable=False),
        sa.Column("service_type", sa.String(length=80), nullable=False),
        sa.Column("urgency", sa.String(length=20), nullable=False),
        sa.Column("interval_hours", sa.Integer(), nullable=False),
        sa.Column("trigger", sa.String(length=50), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_follow_up_policies_follow_up_policies_effective_range",
        ),
        sa.CheckConstraint(
            "interval_hours > 0", name="ck_follow_up_policies_follow_up_policies_interval_positive"
        ),
    )
    op.create_index(
        "ix_follow_up_policies_lookup",
        "follow_up_policies",
        ["service_type", "urgency", "effective_from"],
        unique=False,
    )
    op.create_table(
        "contact_attempt_policies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "follow_up_policy_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("follow_up_policies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("spacing_hours", sa.Integer(), nullable=False),
        sa.Column("safe_callback_start", sa.Time(timezone=False)),
        sa.Column("safe_callback_end", sa.Time(timezone=False)),
        sa.Column("alternative_channel", sa.String(length=30)),
        sa.CheckConstraint(
            "spacing_hours > 0",
            name="ck_contact_attempt_policies_contact_attempt_policies_spacing_positive",
        ),
        sa.CheckConstraint(
            "max_attempts > 0",
            name="ck_contact_attempt_policies_contact_attempt_policies_max_attempts_positive",
        ),
    )
    op.create_index(
        "ix_contact_attempt_policies_follow_up_policy_id",
        "contact_attempt_policies",
        ["follow_up_policy_id"],
        unique=False,
    )
    op.create_table(
        "follow_ups",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "referral_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("referrals.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "follow_up_policy_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("follow_up_policies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "contact_attempt_policy_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contact_attempt_policies.id", ondelete="RESTRICT"),
        ),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=25), nullable=False, server_default=sa.text("'DUE'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('DUE','IN_PROGRESS','COMPLETED','CANCELLED','OPTED_OUT')",
            name="ck_follow_ups_follow_ups_status",
        ),
    )
    op.create_index("ix_follow_ups_due", "follow_ups", ["status", "due_at"], unique=False)
    op.create_table(
        "contact_attempts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "follow_up_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("follow_ups.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(length=30), nullable=False),
        sa.Column(
            "attempted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("outcome", sa.String(length=30), nullable=False),
        sa.Column("safe_contact_check", sa.String(length=25), nullable=False),
        sa.Column(
            "policy_reference",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contact_attempt_policies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("notes_reference", sa.String(length=500)),
        sa.CheckConstraint(
            "safe_contact_check IN ('PASSED','FAILED','NOT_PERFORMED')",
            name="ck_contact_attempts_contact_attempts_safe_contact_check",
        ),
    )
    op.create_index(
        "ix_contact_attempts_follow_up_time",
        "contact_attempts",
        ["follow_up_id", "attempted_at"],
        unique=False,
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER referral_events_append_only BEFORE UPDATE ON referral_events FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER resource_verifications_append_only BEFORE UPDATE ON resource_verifications FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER support_outcomes_append_only BEFORE UPDATE ON support_outcomes FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TRIGGER IF EXISTS support_outcomes_append_only ON support_outcomes"))
    op.execute(
        sa.text(
            "DROP TRIGGER IF EXISTS resource_verifications_append_only ON resource_verifications"
        )
    )
    op.execute(sa.text("DROP TRIGGER IF EXISTS referral_events_append_only ON referral_events"))
    op.drop_table("contact_attempts")
    op.drop_table("follow_ups")
    op.drop_table("contact_attempt_policies")
    op.drop_table("follow_up_policies")
    op.drop_table("support_outcomes")
    op.drop_table("referral_events")
    op.drop_table("referrals")
    op.drop_table("resource_verifications")
    op.drop_table("service_resources")
