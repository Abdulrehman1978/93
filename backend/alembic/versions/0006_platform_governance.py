"""Create platform governance tables from an immutable schema snapshot."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0006_platform_governance"
down_revision = "0005_resources_referrals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "async_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("job_type", sa.String(length=80), nullable=False),
        sa.Column("payload_reference", sa.String(length=500), nullable=False),
        sa.Column("payload_metadata", postgresql.JSONB()),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default=sa.text("'QUEUED'")
        ),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("100")),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column(
            "available_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("locked_at", sa.DateTime(timezone=True)),
        sa.Column("locked_by", sa.String(length=255)),
        sa.Column("last_error_class", sa.String(length=100)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("priority >= 0", name="ck_async_jobs_async_jobs_priority_nonnegative"),
        sa.CheckConstraint(
            "attempts >= 0 AND max_attempts > 0 AND attempts <= max_attempts",
            name="ck_async_jobs_async_jobs_attempt_bounds",
        ),
        sa.CheckConstraint(
            "status IN ('QUEUED','RUNNING','SUCCEEDED','FAILED','CANCELLED')",
            name="ck_async_jobs_async_jobs_status",
        ),
    )
    op.create_index(
        "ix_async_jobs_claim", "async_jobs", ["status", "available_at", "priority"], unique=False
    )
    op.create_table(
        "integration_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("direction", sa.String(length=15), nullable=False),
        sa.Column("external_event_key", sa.String(length=255)),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default=sa.text("'RECEIVED'")
        ),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True)),
        sa.Column("payload_reference", sa.String(length=500)),
        sa.Column("payload_metadata", postgresql.JSONB()),
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
        sa.UniqueConstraint(
            "provider", "direction", "external_event_key", name="uq_integration_events_external_key"
        ),
        sa.CheckConstraint(
            "direction IN ('INBOUND','OUTBOUND')",
            name="ck_integration_events_integration_events_direction",
        ),
        sa.CheckConstraint(
            "status IN ('RECEIVED','PROCESSING','SUCCEEDED','FAILED','IGNORED')",
            name="ck_integration_events_integration_events_status",
        ),
        sa.CheckConstraint(
            "attempt_count >= 0",
            name="ck_integration_events_integration_events_attempt_nonnegative",
        ),
        sa.UniqueConstraint("idempotency_key", name="uq_integration_events_idempotency_key"),
    )
    op.create_index(
        "ix_integration_events_next_attempt",
        "integration_events",
        ["status", "next_attempt_at"],
        unique=False,
    )
    op.create_table(
        "audit_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("actor_reference", sa.String(length=255)),
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
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=255), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("correlation_id", sa.String(length=255)),
        sa.Column("safe_metadata", postgresql.JSONB()),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_audit_events_entity_time",
        "audit_events",
        ["entity_type", "entity_id", "occurred_at"],
        unique=False,
    )
    op.create_index("ix_audit_events_occurred_at", "audit_events", ["occurred_at"], unique=False)
    op.create_table(
        "deletion_requests",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("object_type", sa.String(length=100), nullable=False),
        sa.Column("object_id", sa.String(length=255), nullable=False),
        sa.Column(
            "state",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'DELETION_REQUESTED'"),
        ),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("authority", sa.String(length=255), nullable=False),
        sa.Column("source_class", sa.String(length=80), nullable=False),
        sa.Column("new_expiry", sa.DateTime(timezone=True)),
        sa.Column("approver_reference", sa.String(length=255)),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "state <> 'DELETION_VERIFIED' OR completed_at IS NOT NULL",
            name="ck_deletion_requests_deletion_requests_verified_requires_completion",
        ),
        sa.CheckConstraint(
            "state IN ('DELETION_REQUESTED','PRIMARY_OBJECT_DELETED','RETENTION_HOLD','BACKUP_EXPIRY_PENDING','DELETION_VERIFIED')",
            name="ck_deletion_requests_deletion_requests_state",
        ),
    )
    op.create_index(
        "ix_deletion_requests_state", "deletion_requests", ["state", "requested_at"], unique=False
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER audit_events_append_only BEFORE UPDATE ON audit_events FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TRIGGER IF EXISTS audit_events_append_only ON audit_events"))
    op.drop_table("deletion_requests")
    op.drop_table("audit_events")
    op.drop_table("integration_events")
    op.drop_table("async_jobs")
