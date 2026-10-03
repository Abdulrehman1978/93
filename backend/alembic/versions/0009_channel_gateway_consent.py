"""Add the canonical channel gateway and interaction-scoped consent ledger."""

import sqlalchemy as sa

from alembic import op

revision = "0009_channel_gateway_consent"
down_revision = "0008_auth_trust_boundary"
branch_labels = None
depends_on = None


def _drop_constraint(table: str, name: str) -> None:
    """Drop a historical constraint without Alembic naming-convention rewriting."""
    op.execute(sa.text(f'ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{name}"'))


def upgrade() -> None:
    # Existing interaction rows are preserved. The subject is derived from the
    # already-required case relation before that relation becomes optional.
    op.add_column("interactions", sa.Column("subject_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_interactions_subject_id_subjects",
        "interactions",
        "subjects",
        ["subject_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.add_column(
        "interactions",
        sa.Column(
            "interaction_mode",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'UNSELECTED'"),
        ),
    )
    op.add_column("interactions", sa.Column("session_token_digest", sa.String(length=64)))
    op.add_column("interactions", sa.Column("session_expires_at", sa.DateTime(timezone=True)))
    op.add_column("interactions", sa.Column("last_activity_at", sa.DateTime(timezone=True)))
    op.add_column("interactions", sa.Column("session_policy_version", sa.String(length=80)))

    op.execute(
        sa.text(
            """
            UPDATE interactions AS i
            SET subject_id = c.subject_id
            FROM cases AS c
            WHERE i.case_id = c.id AND i.subject_id IS NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE interactions
            SET channel = CASE channel
                WHEN 'VOICE' THEN 'WEB'
                WHEN 'TEXT' THEN 'WEB'
                WHEN 'SILENT' THEN 'WEB'
                WHEN 'IVR' THEN 'IVR'
                WHEN 'CHATBOT' THEN 'CHATBOT'
                WHEN 'PORTAL' THEN 'PORTAL'
                WHEN 'MOBILE' THEN 'MOBILE'
                ELSE channel
            END,
            interaction_mode = CASE channel
                WHEN 'VOICE' THEN 'VOICE'
                WHEN 'TEXT' THEN 'TEXT'
                WHEN 'SILENT' THEN 'SILENT'
                WHEN 'IVR' THEN 'VOICE'
                WHEN 'CHATBOT' THEN 'TEXT'
                ELSE 'UNSELECTED'
            END
            """
        )
    )
    op.alter_column("interactions", "subject_id", nullable=False)
    _drop_constraint("interactions", "ck_interactions_ck_interactions_interactions_channel")
    op.create_check_constraint(
        "interactions_channel",
        "interactions",
        "channel IN ('WEB','PORTAL','IVR','TELEPHONY','CHATBOT','MOBILE','OPERATOR','SYSTEM')",
    )
    op.create_check_constraint(
        "interactions_interaction_mode",
        "interactions",
        "interaction_mode IN ('UNSELECTED','VOICE','TEXT','SILENT')",
    )
    op.alter_column("interactions", "case_id", nullable=True)

    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION validate_channel_metadata(payload jsonb)
            RETURNS boolean
            LANGUAGE plpgsql
            IMMUTABLE
            AS $$
            DECLARE key_name text;
            BEGIN
                IF payload IS NULL THEN RETURN true; END IF;
                FOR key_name IN SELECT jsonb_object_keys(payload) LOOP
                    IF key_name NOT IN (
                        'provider_code', 'provider_session_reference',
                        'protocol_version', 'capability_flags',
                        'external_reference', 'client_request_id'
                    ) THEN
                        RETURN false;
                    END IF;
                END LOOP;
                RETURN true;
            END;
            $$
            """
        )
    )
    op.create_check_constraint(
        "interactions_channel_metadata_allowlist",
        "interactions",
        "channel_metadata IS NULL OR validate_channel_metadata(channel_metadata)",
    )
    op.create_check_constraint(
        "interactions_session_timestamps",
        "interactions",
        "session_token_digest IS NULL OR (session_expires_at IS NOT NULL AND last_activity_at IS NOT NULL)",
    )
    op.create_index("ix_interactions_subject_started", "interactions", ["subject_id", "started_at"])
    op.create_index(
        "ix_interactions_active_expiry", "interactions", ["status", "session_expires_at"]
    )
    op.create_index(
        "uq_interactions_session_token_digest",
        "interactions",
        ["session_token_digest"],
        unique=True,
        postgresql_where=sa.text("session_token_digest IS NOT NULL"),
    )
    op.create_index(
        "uq_interactions_channel_external_reference",
        "interactions",
        ["channel", "external_reference"],
        unique=True,
        postgresql_where=sa.text("external_reference IS NOT NULL"),
    )

    op.add_column("consent_events", sa.Column("interaction_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "fk_consent_events_interaction_id_interactions",
        "consent_events",
        "interactions",
        ["interaction_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.add_column("consent_events", sa.Column("action_id", sa.String(length=255)))
    op.add_column("consent_events", sa.Column("served_locale", sa.String(length=20)))
    op.add_column("consent_events", sa.Column("translation_status", sa.String(length=30)))
    op.execute(
        sa.text("UPDATE consent_events SET channel = 'WEB' WHERE channel IN ('VOICE','TEXT')")
    )
    _drop_constraint(
        "consent_events", "ck_consent_events_ck_consent_events_consent_events_channel"
    )
    op.create_check_constraint(
        "consent_events_channel",
        "consent_events",
        "channel IN ('WEB','PORTAL','IVR','TELEPHONY','CHATBOT','MOBILE','OPERATOR','SYSTEM')",
    )
    op.create_check_constraint(
        "consent_events_translation_status",
        "consent_events",
        "translation_status IS NULL OR translation_status IN ('AUTHORITATIVE','HUMAN_VERIFIED','MACHINE_TRANSLATED','FALLBACK_LANGUAGE','NOT_AVAILABLE')",
    )
    op.create_index("ix_consent_events_interaction_id", "consent_events", ["interaction_id"])
    op.create_index(
        "uq_consent_events_interaction_action",
        "consent_events",
        ["interaction_id", "action_id"],
        unique=True,
        postgresql_where=sa.text("interaction_id IS NOT NULL AND action_id IS NOT NULL"),
    )

    op.add_column(
        "processing_authorizations",
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default=sa.text("'ACTIVE'")
        ),
    )
    op.add_column("processing_authorizations", sa.Column("revoked_at", sa.DateTime(timezone=True)))
    op.create_check_constraint(
        "processing_authorizations_status",
        "processing_authorizations",
        "status IN ('ACTIVE','REVOKED','EXPIRED','SUPERSEDED')",
    )
    op.create_check_constraint(
        "processing_authorizations_inactive_timestamp",
        "processing_authorizations",
        "status = 'ACTIVE' OR revoked_at IS NOT NULL OR status = 'EXPIRED'",
    )

    op.execute(
        sa.text(
            """
            CREATE UNIQUE INDEX uq_interaction_events_interaction_source
            ON interaction_events (interaction_id, source_reference)
            WHERE source_reference IS NOT NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            CREATE TRIGGER interaction_events_append_only
            BEFORE UPDATE OR DELETE ON interaction_events
            FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DROP TRIGGER IF EXISTS interaction_events_append_only ON interaction_events")
    )
    op.drop_index("uq_interaction_events_interaction_source", table_name="interaction_events")
    _drop_constraint(
        "processing_authorizations",
        "ck_processing_authorizations_processing_authorizations_inactive_timestamp",
    )
    _drop_constraint(
        "processing_authorizations",
        "ck_processing_authorizations_processing_authorizations_status",
    )
    op.drop_column("processing_authorizations", "revoked_at")
    op.drop_column("processing_authorizations", "status")
    op.drop_index("uq_consent_events_interaction_action", table_name="consent_events")
    op.drop_index("ix_consent_events_interaction_id", table_name="consent_events")
    _drop_constraint("consent_events", "ck_consent_events_consent_events_translation_status")
    _drop_constraint("consent_events", "ck_consent_events_consent_events_channel")
    op.create_check_constraint(
        "ck_consent_events_consent_events_channel",
        "consent_events",
        "channel IN ('PORTAL','VOICE','TEXT','IVR','OPERATOR','SYSTEM')",
    )
    _drop_constraint("consent_events", "fk_consent_events_interaction_id_interactions")
    op.drop_column("consent_events", "translation_status")
    op.drop_column("consent_events", "served_locale")
    op.drop_column("consent_events", "action_id")
    op.drop_column("consent_events", "interaction_id")
    op.drop_index("uq_interactions_channel_external_reference", table_name="interactions")
    op.drop_index("uq_interactions_session_token_digest", table_name="interactions")
    op.drop_index("ix_interactions_active_expiry", table_name="interactions")
    op.drop_index("ix_interactions_subject_started", table_name="interactions")
    _drop_constraint("interactions", "ck_interactions_interactions_session_timestamps")
    _drop_constraint("interactions", "ck_interactions_interactions_channel_metadata_allowlist")
    op.execute(sa.text("DROP FUNCTION IF EXISTS validate_channel_metadata(jsonb)"))
    _drop_constraint("interactions", "ck_interactions_interactions_interaction_mode")
    _drop_constraint("interactions", "ck_interactions_interactions_channel")
    op.create_check_constraint(
        "ck_interactions_interactions_channel",
        "interactions",
        "channel IN ('VOICE','TEXT','SILENT','IVR','CHATBOT','PORTAL','MOBILE')",
    )
    op.alter_column("interactions", "case_id", nullable=False)
    op.drop_column("interactions", "session_policy_version")
    op.drop_column("interactions", "last_activity_at")
    op.drop_column("interactions", "session_expires_at")
    op.drop_column("interactions", "session_token_digest")
    op.drop_column("interactions", "interaction_mode")
    _drop_constraint("interactions", "fk_interactions_subject_id_subjects")
    op.drop_column("interactions", "subject_id")
