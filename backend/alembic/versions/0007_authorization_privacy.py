"""Add the Packet 04 authorization, identity, and privacy foundation.

This revision is a self-contained snapshot. It intentionally leaves Packet 03
revisions untouched and adds only five security tables plus actor identity
foreign keys and encrypted-value metadata fields.
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0007_authorization_privacy"
down_revision = "0006_platform_governance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "actors",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("actor_type", sa.String(length=30), nullable=False),
        sa.Column("display_reference", sa.String(length=255), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default=sa.text("'ACTIVE'")
        ),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True)),
        sa.Column("jurisdiction_id", postgresql.UUID(as_uuid=True)),
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
            "actor_type IN ('STAFF','SERVICE_PROVIDER','CITIZEN','SYSTEM','AUDITOR')",
            name="ck_actors_actors_type",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE','SUSPENDED','DISABLED')", name="ck_actors_actors_status"
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_actors_organization_id_organizations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["jurisdiction_id"],
            ["jurisdictions.id"],
            name="fk_actors_jurisdiction_id_jurisdictions",
            ondelete="RESTRICT",
        ),
    )
    op.create_index(
        "ix_actors_scope", "actors", ["organization_id", "jurisdiction_id", "status"], unique=False
    )

    op.create_table(
        "actor_identities",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_code", sa.String(length=80), nullable=False),
        sa.Column("issuer", sa.String(length=500), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default=sa.text("'ACTIVE'")
        ),
        sa.UniqueConstraint("issuer", "subject", name="uq_actor_identities_issuer_subject"),
        sa.CheckConstraint(
            "status IN ('ACTIVE','REVOKED')", name="ck_actor_identities_actor_identities_status"
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["actors.id"],
            name="fk_actor_identities_actor_id_actors",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_actor_identities_actor_id", "actor_identities", ["actor_id"], unique=False)
    op.create_index(
        "ix_actor_identities_provider_subject",
        "actor_identities",
        ["provider_code", "subject"],
        unique=False,
    )

    op.create_table(
        "roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default=sa.text("'ACTIVE'")
        ),
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
        sa.CheckConstraint("status IN ('ACTIVE','DISABLED')", name="ck_roles_roles_status"),
        sa.UniqueConstraint("code", name="uq_roles_code"),
    )

    op.create_table(
        "actor_role_bindings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True)),
        sa.Column("jurisdiction_id", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "effective_from",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("effective_to", sa.DateTime(timezone=True)),
        sa.Column("granted_by_actor_id", postgresql.UUID(as_uuid=True)),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("policy_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_actor_role_bindings_actor_role_bindings_effective_range",
        ),
        sa.CheckConstraint(
            "granted_by_actor_id IS NULL OR granted_by_actor_id <> actor_id",
            name="ck_actor_role_bindings_actor_role_bindings_no_self_grant",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["actors.id"],
            name="fk_actor_role_bindings_actor_id_actors",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_actor_role_bindings_role_id_roles",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_actor_role_bindings_organization_id_organizations",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["jurisdiction_id"],
            ["jurisdictions.id"],
            name="fk_actor_role_bindings_jurisdiction_id_jurisdictions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["granted_by_actor_id"],
            ["actors.id"],
            name="fk_actor_role_bindings_granted_by_actor_id_actors",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["policy_version_id"],
            ["policy_versions.id"],
            name="fk_actor_role_bindings_policy_version_id_policy_versions",
            ondelete="RESTRICT",
        ),
    )
    op.create_index(
        "ix_actor_role_bindings_active",
        "actor_role_bindings",
        ["actor_id", "effective_from", "effective_to"],
        unique=False,
    )
    op.create_index(
        "ix_actor_role_bindings_scope",
        "actor_role_bindings",
        ["organization_id", "jurisdiction_id", "role_id"],
        unique=False,
    )

    op.create_table(
        "access_elevations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=False),
        sa.Column("resource_id", sa.String(length=255)),
        sa.Column("case_id", postgresql.UUID(as_uuid=True)),
        sa.Column("requested_permission", sa.String(length=120), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("policy_source", sa.String(length=80), nullable=False),
        sa.Column("approved_by_actor_id", postgresql.UUID(as_uuid=True)),
        sa.Column(
            "effective_from",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default=sa.text("'ACTIVE'")
        ),
        sa.Column("correlation_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "case_id IS NOT NULL OR resource_id IS NOT NULL",
            name="ck_access_elevations_access_elevations_scope_required",
        ),
        sa.CheckConstraint(
            "expires_at > effective_from", name="ck_access_elevations_access_elevations_expiry"
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE','EXPIRED','REVOKED')",
            name="ck_access_elevations_access_elevations_status",
        ),
        sa.CheckConstraint(
            "approved_by_actor_id IS NULL OR approved_by_actor_id <> actor_id",
            name="ck_access_elevations_access_elevations_no_self_approval",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["actors.id"],
            name="fk_access_elevations_actor_id_actors",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["cases.id"],
            name="fk_access_elevations_case_id_cases",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["approved_by_actor_id"],
            ["actors.id"],
            name="fk_access_elevations_approved_by_actor_id_actors",
            ondelete="RESTRICT",
        ),
    )
    op.create_index(
        "ix_access_elevations_active",
        "access_elevations",
        ["actor_id", "status", "expires_at"],
        unique=False,
    )
    op.create_index("ix_access_elevations_case_id", "access_elevations", ["case_id"], unique=False)

    role_table = sa.table(
        "roles",
        sa.column("code", sa.String(length=80)),
        sa.column("display_name", sa.String(length=255)),
        sa.column("description", sa.Text()),
    )
    op.bulk_insert(
        role_table,
        [
            {
                "code": code,
                "display_name": code.replace("_", " ").title(),
                "description": "Packet 04 role catalog entry.",
            }
            for code in (
                "HELPLINE_OPERATOR",
                "SUPERVISOR",
                "CASE_OFFICER",
                "COUNSELLOR",
                "LEGAL_SUPPORT",
                "MEDICAL_SUPPORT",
                "DISTRICT_OFFICER",
                "STATE_ADMIN",
                "MINISTRY_ADMIN",
                "AUDITOR",
                "SYSTEM_ADMIN",
            )
        ],
    )

    _rename_and_add_actor_column(
        "case_participants", "participant_reference", "external_actor_reference", "actor_id"
    )
    _rename_and_add_actor_column(
        "case_status_events", "actor_reference", "external_actor_reference", "actor_id"
    )
    _rename_and_add_actor_column(
        "consent_events", "actor_reference", "external_actor_reference", "actor_id"
    )
    _rename_and_add_actor_column(
        "processing_authorizations", "actor_reference", "external_actor_reference", "actor_id"
    )
    _rename_and_add_actor_column(
        "assessment_reviews",
        "actor_reference",
        "external_actor_reference",
        "actor_id",
        make_external_nullable=True,
    )
    _rename_and_add_actor_column(
        "referral_events", "actor_reference", "external_actor_reference", "actor_id"
    )
    _rename_and_add_actor_column(
        "resource_verifications",
        "verified_by",
        "external_verifier_reference",
        "verified_by_actor_id",
        make_external_nullable=True,
    )
    _rename_and_add_actor_column(
        "support_outcomes", "verified_by", "external_verifier_reference", "verified_by_actor_id"
    )
    _rename_and_add_actor_column(
        "audit_events", "actor_reference", "external_actor_reference", "actor_id"
    )
    _rename_and_add_actor_column(
        "deletion_requests",
        "approver_reference",
        "external_approver_reference",
        "approver_actor_id",
    )

    op.add_column(
        "referrals", sa.Column("assigned_provider_actor_id", postgresql.UUID(as_uuid=True))
    )
    op.create_foreign_key(
        "fk_referrals_assigned_provider_actor_id_actors",
        "referrals",
        "actors",
        ["assigned_provider_actor_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_referrals_assigned_provider_actor_id",
        "referrals",
        ["assigned_provider_actor_id"],
        unique=False,
    )

    op.add_column("audit_events", sa.Column("decision", sa.String(length=10)))
    op.add_column("audit_events", sa.Column("reason_code", sa.String(length=100)))
    op.add_column("audit_events", sa.Column("purpose", sa.String(length=80)))
    op.add_column("audit_events", sa.Column("policy_version_id", postgresql.UUID(as_uuid=True)))
    op.create_foreign_key(
        "fk_audit_events_policy_version_id_policy_versions",
        "audit_events",
        "policy_versions",
        ["policy_version_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.execute(
        sa.text(
            "CREATE TRIGGER audit_events_append_only_delete BEFORE DELETE ON audit_events FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )


def _rename_and_add_actor_column(
    table: str,
    old_name: str,
    external_name: str,
    actor_name: str,
    *,
    make_external_nullable: bool = False,
) -> None:
    op.alter_column(
        table,
        old_name,
        existing_type=sa.String(length=255),
        new_column_name=external_name,
        nullable=make_external_nullable or table != "assessment_reviews",
    )
    op.add_column(table, sa.Column(actor_name, postgresql.UUID(as_uuid=True)))
    op.create_foreign_key(
        f"fk_{table}_{actor_name}_actors",
        table,
        "actors",
        [actor_name],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(f"ix_{table}_{actor_name}", table, [actor_name], unique=False)


def downgrade() -> None:
    op.execute(sa.text("DROP TRIGGER IF EXISTS audit_events_append_only_delete ON audit_events"))
    op.drop_constraint(
        "fk_audit_events_policy_version_id_policy_versions", "audit_events", type_="foreignkey"
    )
    op.drop_column("audit_events", "policy_version_id")
    op.drop_column("audit_events", "purpose")
    op.drop_column("audit_events", "reason_code")
    op.drop_column("audit_events", "decision")

    op.drop_index("ix_referrals_assigned_provider_actor_id", table_name="referrals")
    op.drop_constraint(
        "fk_referrals_assigned_provider_actor_id_actors", "referrals", type_="foreignkey"
    )
    op.drop_column("referrals", "assigned_provider_actor_id")

    for table, external, old, actor in (
        (
            "deletion_requests",
            "external_approver_reference",
            "approver_reference",
            "approver_actor_id",
        ),
        ("audit_events", "external_actor_reference", "actor_reference", "actor_id"),
        ("support_outcomes", "external_verifier_reference", "verified_by", "verified_by_actor_id"),
        (
            "resource_verifications",
            "external_verifier_reference",
            "verified_by",
            "verified_by_actor_id",
        ),
        ("referral_events", "external_actor_reference", "actor_reference", "actor_id"),
        ("assessment_reviews", "external_actor_reference", "actor_reference", "actor_id"),
        ("processing_authorizations", "external_actor_reference", "actor_reference", "actor_id"),
        ("consent_events", "external_actor_reference", "actor_reference", "actor_id"),
        ("case_status_events", "external_actor_reference", "actor_reference", "actor_id"),
        ("case_participants", "external_actor_reference", "participant_reference", "actor_id"),
    ):
        op.drop_index(f"ix_{table}_{actor}", table_name=table)
        op.drop_constraint(f"fk_{table}_{actor}_actors", table, type_="foreignkey")
        op.drop_column(table, actor)
        op.alter_column(
            table,
            external,
            existing_type=sa.String(length=255),
            new_column_name=old,
            nullable=table not in {"assessment_reviews", "resource_verifications"},
        )

    op.drop_index("ix_access_elevations_case_id", table_name="access_elevations")
    op.drop_index("ix_access_elevations_active", table_name="access_elevations")
    op.drop_table("access_elevations")
    op.drop_index("ix_actor_role_bindings_scope", table_name="actor_role_bindings")
    op.drop_index("ix_actor_role_bindings_active", table_name="actor_role_bindings")
    op.drop_table("actor_role_bindings")
    op.drop_table("roles")
    op.drop_index("ix_actor_identities_provider_subject", table_name="actor_identities")
    op.drop_index("ix_actor_identities_actor_id", table_name="actor_identities")
    op.drop_table("actor_identities")
    op.drop_index("ix_actors_scope", table_name="actors")
    op.drop_table("actors")
