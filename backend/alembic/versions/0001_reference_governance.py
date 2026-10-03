"""Create reference and policy catalogs from an immutable schema snapshot."""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_reference_governance"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
    op.create_table(
        "jurisdictions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("level", sa.String(length=30), nullable=False),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("jurisdictions.id", ondelete="RESTRICT"),
        ),
        sa.Column("boundary_ref", sa.String(length=255)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "level IN ('NATIONAL','STATE','DISTRICT','TALUKA','LOCAL')",
            name="ck_jurisdictions_jurisdictions_level",
        ),
        sa.UniqueConstraint("code", name="uq_jurisdictions_code"),
    )
    op.create_index("ix_jurisdictions_parent_id", "jurisdictions", ["parent_id"], unique=False)
    op.create_table(
        "organizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("org_type", sa.String(length=50), nullable=False),
        sa.Column(
            "jurisdiction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("jurisdictions.id", ondelete="RESTRICT"),
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
        sa.UniqueConstraint("code", name="uq_organizations_code"),
        sa.CheckConstraint(
            "org_type IN ('MINISTRY','HELPLINE_OPERATOR','LEGAL_AID','HEALTH_SERVICE','EMERGENCY_DISPATCH','DISTRICT_ADMIN','SERVICE_PROVIDER')",
            name="ck_organizations_organizations_org_type",
        ),
    )
    op.create_index(
        "ix_organizations_jurisdiction_id", "organizations", ["jurisdiction_id"], unique=False
    )
    op.create_table(
        "policy_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("policy_type", sa.String(length=50), nullable=False),
        sa.Column("version_code", sa.String(length=80), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "policy_type IN ('SAFETY_ESCALATION','SVI_TRIAGE','URGENCY','CONSENT_NOTICE','FOLLOW_UP','RETENTION_SCHEDULE','REFERRAL')",
            name="ck_policy_versions_policy_versions_type",
        ),
        sa.UniqueConstraint("version_code", name="uq_policy_versions_version_code"),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_policy_versions_policy_versions_effective_range",
        ),
    )
    op.create_table(
        "processing_authority_types",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("authority_code", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("authority_source_class", sa.String(length=50), nullable=False),
        sa.Column("legal_reference", sa.String(length=500), nullable=False),
        sa.Column(
            "jurisdiction", sa.String(length=100), nullable=False, server_default=sa.text("'IN'")
        ),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_to", sa.DateTime(timezone=True)),
        sa.Column(
            "status", sa.String(length=30), nullable=False, server_default=sa.text("'ACTIVE'")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "authority_source_class IN ('STATUTORY','REGULATORY','CONSTITUTIONAL','EXECUTIVE_POLICY','PRODUCT_POLICY')",
            name="ck_processing_authority_types_processing_authority_types_authority_source_class",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE','SUPERSEDED','REVOKED')",
            name="ck_processing_authority_types_processing_authority_types_status",
        ),
        sa.UniqueConstraint("authority_code", name="uq_processing_authority_types_authority_code"),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_processing_authority_types_processing_authority_types_effective_range",
        ),
    )
    op.create_index(
        "ix_processing_authority_types_jurisdiction_status",
        "processing_authority_types",
        ["jurisdiction", "status"],
        unique=False,
    )
    op.create_table(
        "processing_purposes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("purpose_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "default_authority_code",
            sa.String(length=80),
            sa.ForeignKey("processing_authority_types.authority_code", ondelete="RESTRICT"),
        ),
        sa.Column(
            "policy_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("policy_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("purpose_code", name="uq_processing_purposes_purpose_code"),
    )
    op.create_index(
        "ix_processing_purposes_policy_version_id",
        "processing_purposes",
        ["policy_version_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("processing_purposes")
    op.drop_table("processing_authority_types")
    op.drop_table("policy_versions")
    op.drop_table("organizations")
    op.drop_table("jurisdictions")
