"""Harden Packet 06 consent authority and seed immutable reference data."""

import sqlalchemy as sa

from alembic import op

revision = "0010_packet06_consent_hardening"
down_revision = "0009_channel_gateway_consent"
branch_labels = None
depends_on = None

POLICY_HASH = "2797c4f4dc666e141b53098551d3129df297ce0a4fc7eea024e2f3f718674dc3"
EFFECTIVE = "2026-10-03 00:00:00+00"


def upgrade() -> None:
    # Consent is an immutable ledger in both directions.
    op.execute(sa.text("DROP TRIGGER IF EXISTS consent_events_append_only ON consent_events"))
    op.execute(
        sa.text(
            "CREATE TRIGGER consent_events_append_only BEFORE UPDATE OR DELETE ON consent_events "
            "FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )
    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_processing_authorizations_active_interaction_authority "
            "ON processing_authorizations (interaction_id, processing_purpose_id, authority_type_id) "
            "WHERE interaction_id IS NOT NULL AND status = 'ACTIVE'"
        )
    )

    op.execute(
        sa.text("""
        INSERT INTO policy_versions
            (policy_type, version_code, content_hash, effective_from, is_active)
        VALUES ('CONSENT_NOTICE', 'packet-06-consent-v1', :hash, CAST(:effective AS timestamptz), true)
        ON CONFLICT (version_code) DO UPDATE SET
            policy_type = EXCLUDED.policy_type,
            content_hash = EXCLUDED.content_hash,
            effective_from = EXCLUDED.effective_from,
            is_active = true
    """).bindparams(hash=POLICY_HASH, effective=EFFECTIVE)
    )

    authorities = [
        ("CONSENT", "Consent", "PRODUCT_POLICY", "Documented, purpose-specific consent."),
        ("LEGAL_OBLIGATION", "Legal obligation", "STATUTORY", "Applicable statutory obligation."),
        (
            "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE",
            "Voluntary specified purpose",
            "PRODUCT_POLICY",
            "Information voluntarily provided for the specified service purpose.",
        ),
        (
            "MEDICAL_EMERGENCY",
            "Medical emergency",
            "STATUTORY",
            "Documented emergency processing authority.",
        ),
        (
            "PUBLIC_ORDER_OR_DISASTER_ASSISTANCE",
            "Public order or disaster assistance",
            "STATUTORY",
            "Documented emergency public-order authority.",
        ),
    ]
    for code, name, source_class, reference in authorities:
        op.execute(
            sa.text("""
            INSERT INTO processing_authority_types
                (authority_code, display_name, authority_source_class, legal_reference, effective_from, status)
            VALUES (:code, :name, :source_class, :reference, CAST(:effective AS timestamptz), 'ACTIVE')
            ON CONFLICT (authority_code) DO UPDATE SET
                display_name = EXCLUDED.display_name,
                authority_source_class = EXCLUDED.authority_source_class,
                legal_reference = EXCLUDED.legal_reference,
                effective_from = EXCLUDED.effective_from,
                status = 'ACTIVE'
        """).bindparams(
                code=code,
                name=name,
                source_class=source_class,
                reference=reference,
                effective=EFFECTIVE,
            )
        )

    purposes = [
        (
            "PURP-01",
            "Complaint Intake",
            "To receive and route information the person voluntarily submits.",
            "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE",
        ),
        (
            "PURP-02",
            "Speech Transcription",
            "To transcribe intentionally selected voice input.",
            "CONSENT",
        ),
        (
            "PURP-03",
            "Ephemeral Acoustic Processing",
            "Future transient acoustic processing.",
            "CONSENT",
        ),
        (
            "PURP-06",
            "Raw Audio Retention",
            "Future raw audio retention under a documented lawful basis.",
            "CONSENT",
        ),
        (
            "PURP-08",
            "General Support Referral",
            "A separately chosen support referral purpose.",
            "CONSENT",
        ),
        (
            "PURP-09",
            "Emergency Handoff",
            "A narrowly scoped emergency handoff.",
            "MEDICAL_EMERGENCY",
        ),
        (
            "PURP-16",
            "Research and Service Improvement",
            "A separately chosen future research purpose.",
            "CONSENT",
        ),
    ]
    for code, name, description, authority in purposes:
        op.execute(
            sa.text("""
            INSERT INTO processing_purposes
                (purpose_code, name, description, default_authority_code, policy_version_id, is_active)
            VALUES (:code, :name, :description, :authority,
                (SELECT id FROM policy_versions WHERE version_code = 'packet-06-consent-v1'), true)
            ON CONFLICT (purpose_code) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                default_authority_code = EXCLUDED.default_authority_code,
                policy_version_id = EXCLUDED.policy_version_id,
                is_active = true
        """).bindparams(code=code, name=name, description=description, authority=authority)
        )


def downgrade() -> None:
    op.execute(
        sa.text("DROP INDEX IF EXISTS uq_processing_authorizations_active_interaction_authority")
    )
    op.execute(sa.text("DROP TRIGGER IF EXISTS consent_events_append_only ON consent_events"))
    op.execute(
        sa.text(
            "CREATE TRIGGER consent_events_append_only BEFORE UPDATE ON consent_events "
            "FOR EACH ROW EXECUTE FUNCTION prevent_append_only_update()"
        )
    )
