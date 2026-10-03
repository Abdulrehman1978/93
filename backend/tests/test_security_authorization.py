"""Packet 04 authorization, privacy, and adversarial integration tests."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError, StatementError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app.database import engine
from app.db.models import AuditEvent, SubjectContact, TranscriptSegment, Translation
from app.errors import AppException
from app.logging import StructuredJsonFormatter
from app.security.authorization import AuthorizationService
from app.security.context import AuthorizationContext, IntendedCreationScope
from app.security.encryption import EncryptionError, FieldEncryptor, use_field_encryptor
from app.security.principal import SecurityPrincipal
from app.security.sensitive_access import SensitiveFieldAccessService

pytestmark = pytest.mark.integration


async def _id(connection: AsyncConnection, statement: str, **params: object) -> uuid.UUID:
    return (await connection.execute(text(statement), params)).scalar_one()


async def _security_fixture(connection: AsyncConnection) -> dict[str, uuid.UUID]:
    state_id = await _id(
        connection,
        "INSERT INTO jurisdictions (code, name, level) VALUES ('SEC-STATE', 'Security State', 'STATE') RETURNING id",
    )
    district_id = await _id(
        connection,
        "INSERT INTO jurisdictions (code, name, level, parent_id) VALUES ('SEC-DISTRICT', 'Security District', 'DISTRICT', :parent_id) RETURNING id",
        parent_id=state_id,
    )
    foreign_state_id = await _id(
        connection,
        "INSERT INTO jurisdictions (code, name, level) VALUES ('SEC-STATE-B', 'Security State B', 'STATE') RETURNING id",
    )
    foreign_district_id = await _id(
        connection,
        "INSERT INTO jurisdictions (code, name, level, parent_id) VALUES ('SEC-DISTRICT-B', 'Security District B', 'DISTRICT', :parent_id) RETURNING id",
        parent_id=foreign_state_id,
    )
    org_a = await _id(
        connection,
        "INSERT INTO organizations (code, name, org_type, jurisdiction_id) VALUES ('SEC-ORG-A', 'Security Org A', 'HELPLINE_OPERATOR', :jurisdiction_id) RETURNING id",
        jurisdiction_id=district_id,
    )
    org_b = await _id(
        connection,
        "INSERT INTO organizations (code, name, org_type, jurisdiction_id) VALUES ('SEC-ORG-B', 'Security Org B', 'SERVICE_PROVIDER', :jurisdiction_id) RETURNING id",
        jurisdiction_id=foreign_district_id,
    )
    policy_id = await _id(
        connection,
        "INSERT INTO policy_versions (policy_type, version_code, content_hash, effective_from) VALUES ('REFERRAL', 'SEC-PACKET04-POLICY', repeat('b', 64), now()) RETURNING id",
    )
    authority_id = await _id(
        connection,
        "INSERT INTO processing_authority_types (authority_code, display_name, authority_source_class, legal_reference, effective_from) VALUES ('SEC-AUTHORITY', 'Security authority', 'STATUTORY', 'SEC-REF', now()) RETURNING id",
    )
    purpose_id = await _id(
        connection,
        "INSERT INTO processing_purposes (purpose_code, name, description, default_authority_code, policy_version_id) VALUES ('CASE_SUPPORT', 'Case support', 'Synthetic test purpose', 'SEC-AUTHORITY', :policy_id) RETURNING id",
        policy_id=policy_id,
    )
    subject_id = await _id(
        connection,
        "INSERT INTO subjects (subject_reference, classification, synthetic_marker) VALUES ('SEC-SUBJECT', 'SYNTHETIC', 'SYNTHETIC_DEMO') RETURNING id",
    )
    unassigned_subject_id = await _id(
        connection,
        "INSERT INTO subjects (subject_reference, classification, synthetic_marker) VALUES ('SEC-SUBJECT-B', 'SYNTHETIC', 'SYNTHETIC_DEMO') RETURNING id",
    )
    foreign_subject_id = await _id(
        connection,
        "INSERT INTO subjects (subject_reference, classification, synthetic_marker) VALUES ('SEC-SUBJECT-C', 'SYNTHETIC', 'SYNTHETIC_DEMO') RETURNING id",
    )
    case_id = await _id(
        connection,
        "INSERT INTO cases (public_tracking_id, subject_id, organization_id, jurisdiction_id) VALUES ('SEC-CASE-A', :subject_id, :org_id, :jurisdiction_id) RETURNING id",
        subject_id=subject_id,
        org_id=org_a,
        jurisdiction_id=district_id,
    )
    foreign_case_id = await _id(
        connection,
        "INSERT INTO cases (public_tracking_id, subject_id, organization_id, jurisdiction_id) VALUES ('SEC-CASE-C', :subject_id, :org_id, :jurisdiction_id) RETURNING id",
        subject_id=foreign_subject_id,
        org_id=org_b,
        jurisdiction_id=foreign_district_id,
    )
    unassigned_case_id = await _id(
        connection,
        "INSERT INTO cases (public_tracking_id, subject_id, organization_id, jurisdiction_id) VALUES ('SEC-CASE-B', :subject_id, :org_id, :jurisdiction_id) RETURNING id",
        subject_id=unassigned_subject_id,
        org_id=org_a,
        jurisdiction_id=district_id,
    )
    authorization_id = await _id(
        connection,
        "INSERT INTO processing_authorizations (case_id, processing_purpose_id, authority_type_id, authorization_reason, policy_version_id) VALUES (:case_id, :purpose_id, :authority_id, 'Synthetic security authorization', :policy_id) RETURNING id",
        case_id=case_id,
        purpose_id=purpose_id,
        authority_id=authority_id,
        policy_id=policy_id,
    )
    foreign_authorization_id = await _id(
        connection,
        "INSERT INTO processing_authorizations (case_id, processing_purpose_id, authority_type_id, authorization_reason, policy_version_id) VALUES (:case_id, :purpose_id, :authority_id, 'Synthetic foreign authorization', :policy_id) RETURNING id",
        case_id=foreign_case_id,
        purpose_id=purpose_id,
        authority_id=authority_id,
        policy_id=policy_id,
    )
    interaction_id = await _id(
        connection,
        "INSERT INTO interactions (subject_id, case_id, channel, interaction_mode) "
        "VALUES (:subject_id, :case_id, 'WEB', 'TEXT') RETURNING id",
        subject_id=subject_id,
        case_id=case_id,
    )
    transcript_id = await _id(
        connection,
        "INSERT INTO transcript_segments (interaction_id, sequence, start_ms, end_ms, language, content) VALUES (:interaction_id, 0, 0, 100, 'en', 'scope-only fixture') RETURNING id",
        interaction_id=interaction_id,
    )

    actors: dict[str, uuid.UUID] = {}
    for key, actor_type, status, organization_id in (
        ("operator", "STAFF", "ACTIVE", org_a),
        ("system_admin", "SYSTEM", "ACTIVE", None),
        ("auditor", "AUDITOR", "ACTIVE", None),
        ("provider", "SERVICE_PROVIDER", "ACTIVE", org_b),
        ("provider_b", "SERVICE_PROVIDER", "ACTIVE", org_b),
        ("district", "STAFF", "ACTIVE", org_a),
        ("expired", "STAFF", "ACTIVE", org_a),
        ("disabled", "STAFF", "DISABLED", org_a),
        ("approver", "STAFF", "ACTIVE", org_a),
    ):
        actors[key] = await _id(
            connection,
            "INSERT INTO actors (actor_type, display_reference, status, organization_id, jurisdiction_id) VALUES (:actor_type, :display_reference, :status, :organization_id, :jurisdiction_id) RETURNING id",
            actor_type=actor_type,
            display_reference=f"SEC-{key}",
            status=status,
            organization_id=organization_id,
            jurisdiction_id=district_id if organization_id else None,
        )

    async def bind(
        actor_key: str,
        role_code: str,
        *,
        organization_id: uuid.UUID | None = org_a,
        jurisdiction_id: uuid.UUID | None = district_id,
        effective_from: str = "now()",
        effective_to: str | None = None,
    ) -> None:
        role_id = await _id(
            connection,
            "SELECT id FROM roles WHERE code = :role_code",
            role_code=role_code,
        )
        expiry_sql = ", effective_to" if effective_to else ""
        expiry_value = f", {effective_to}" if effective_to else ""
        await connection.execute(
            text(
                f"INSERT INTO actor_role_bindings (actor_id, role_id, organization_id, jurisdiction_id, effective_from{expiry_sql}, granted_by_actor_id, reason, policy_version_id) VALUES (:actor_id, :role_id, :organization_id, :jurisdiction_id, {effective_from}{expiry_value}, :grantor, 'Synthetic security binding', :policy_id)"
            ),
            {
                "actor_id": actors[actor_key],
                "role_id": role_id,
                "organization_id": organization_id,
                "jurisdiction_id": jurisdiction_id,
                "grantor": actors["approver"],
                "policy_id": policy_id,
            },
        )

    await bind("operator", "HELPLINE_OPERATOR")
    await bind("system_admin", "SYSTEM_ADMIN", organization_id=None, jurisdiction_id=None)
    await bind("auditor", "AUDITOR", organization_id=None, jurisdiction_id=None)
    await bind("provider", "COUNSELLOR", organization_id=None, jurisdiction_id=None)
    await bind("district", "DISTRICT_OFFICER", organization_id=org_a, jurisdiction_id=state_id)
    await bind(
        "expired",
        "HELPLINE_OPERATOR",
        effective_from="now() - interval '2 hours'",
        effective_to="now() - interval '1 hour'",
    )
    await bind("disabled", "HELPLINE_OPERATOR")

    await connection.execute(
        text(
            "INSERT INTO case_participants (case_id, actor_id, participant_type) VALUES (:case_id, :actor_id, 'OPERATOR')"
        ),
        {"case_id": case_id, "actor_id": actors["operator"]},
    )
    provider_referral_id = await _id(
        connection,
        "INSERT INTO referrals (case_id, service_type, assigned_provider_actor_id, processing_authorization_id, policy_version_id) VALUES (:case_id, 'LEGAL_AID', :provider_id, :authorization_id, :policy_id) RETURNING id",
        case_id=case_id,
        provider_id=actors["provider"],
        authorization_id=authorization_id,
        policy_id=policy_id,
    )
    other_referral_id = await _id(
        connection,
        "INSERT INTO referrals (case_id, service_type, processing_authorization_id, policy_version_id) VALUES (:case_id, 'LEGAL_AID', :authorization_id, :policy_id) RETURNING id",
        case_id=case_id,
        authorization_id=authorization_id,
        policy_id=policy_id,
    )
    foreign_referral_id = await _id(
        connection,
        "INSERT INTO referrals (case_id, service_type, assigned_provider_actor_id, processing_authorization_id, policy_version_id) VALUES (:case_id, 'LEGAL_AID', :provider_id, :authorization_id, :policy_id) RETURNING id",
        case_id=foreign_case_id,
        provider_id=actors["provider_b"],
        authorization_id=foreign_authorization_id,
        policy_id=policy_id,
    )
    return {
        "state_id": state_id,
        "district_id": district_id,
        "foreign_district_id": foreign_district_id,
        "org_a": org_a,
        "org_b": org_b,
        "policy_id": policy_id,
        "subject_id": subject_id,
        "case_id": case_id,
        "unassigned_case_id": unassigned_case_id,
        "foreign_case_id": foreign_case_id,
        "interaction_id": interaction_id,
        "transcript_id": transcript_id,
        "provider_referral_id": provider_referral_id,
        "other_referral_id": other_referral_id,
        "foreign_referral_id": foreign_referral_id,
        "purpose_id": purpose_id,
        **actors,
    }


@pytest.fixture
async def security_data() -> AsyncIterator[
    tuple[AsyncConnection, AsyncSession, dict[str, uuid.UUID]]
]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            yield connection, session, await _security_fixture(connection)
        finally:
            await session.close()
            await transaction.rollback()
            await engine.dispose()


def _principal(actor_id: uuid.UUID, actor_type: str = "STAFF") -> SecurityPrincipal:
    return SecurityPrincipal(
        actor_id=actor_id,
        identity_provider="test-oidc",
        issuer="https://issuer.test",
        external_subject=f"subject-{actor_id}",
        actor_type=actor_type,
    )


def _case_context(case_id: uuid.UUID, **kwargs: object) -> AuthorizationContext:
    return AuthorizationContext.for_resource(
        "case",
        case_id,
        correlation_id="security-test",
        **kwargs,
    )


async def test_horizontal_vertical_and_purpose_boundaries(security_data) -> None:
    _, session, data = security_data
    service = AuthorizationService()
    operator = _principal(data["operator"])

    allowed = await service.authorize(
        operator,
        "case.read.sensitive",
        _case_context(data["case_id"], purpose="CASE_SUPPORT"),
        session,
    )
    assert allowed.allowed

    for action, context in (
        ("unknown.permission", _case_context(data["case_id"])),
        ("case.read.sensitive", _case_context(data["case_id"])),
        (
            "case.read.sensitive",
            _case_context(data["case_id"], purpose="WRONG_PURPOSE"),
        ),
        (
            "case.read.summary",
            _case_context(data["unassigned_case_id"]),
        ),
        (
            "case.read.summary",
            _case_context(
                data["case_id"],
                intended_creation_scope=IntendedCreationScope(organization_id=data["org_b"]),
            ),
        ),
        (
            "case.read.summary",
            _case_context(
                data["case_id"],
                intended_creation_scope=IntendedCreationScope(jurisdiction_id=data["state_id"]),
            ),
        ),
    ):
        decision = await service.authorize(operator, action, context, session)
        assert not decision.allowed, (action, decision.reason_code)

    expired = await service.authorize(
        _principal(data["expired"]),
        "case.read.summary",
        _case_context(data["case_id"]),
        session,
    )
    disabled = await service.authorize(
        _principal(data["disabled"]),
        "case.read.summary",
        _case_context(data["case_id"]),
        session,
    )
    assert not expired.allowed
    assert not disabled.allowed

    admin = await service.authorize(
        _principal(data["system_admin"], "SYSTEM"),
        "case.read.sensitive",
        _case_context(data["case_id"], purpose="CASE_SUPPORT"),
        session,
    )
    auditor = await service.authorize(
        _principal(data["auditor"], "AUDITOR"),
        "transcript.read",
        AuthorizationContext.for_resource(
            "transcript", data["transcript_id"], purpose="CASE_SUPPORT"
        ),
        session,
    )
    audit_allowed = await service.authorize(
        _principal(data["auditor"], "AUDITOR"),
        "audit.read",
        _case_context(data["case_id"]),
        session,
    )
    admin_transcript = await service.authorize(
        _principal(data["system_admin"], "SYSTEM"),
        "transcript.read",
        AuthorizationContext.for_resource(
            "transcript", data["transcript_id"], purpose="CASE_SUPPORT"
        ),
        session,
    )
    assert not admin.allowed
    assert not auditor.allowed
    assert audit_allowed.allowed
    assert not admin_transcript.allowed

    audit_count = await session.scalar(
        select(text("count(*)"))
        .select_from(AuditEvent)
        .where(AuditEvent.actor_id == data["operator"])
    )
    assert audit_count >= 7


async def test_provider_can_only_read_assigned_referral(security_data) -> None:
    _, session, data = security_data
    service = AuthorizationService()
    provider = _principal(data["provider"], "SERVICE_PROVIDER")
    assigned = await service.authorize(
        provider,
        "referral.read",
        AuthorizationContext.for_resource(
            "referral",
            data["provider_referral_id"],
            purpose="CASE_SUPPORT",
            correlation_id="provider-assigned",
        ),
        session,
    )
    unrelated = await service.authorize(
        provider,
        "referral.read",
        AuthorizationContext.for_resource(
            "referral",
            data["other_referral_id"],
            purpose="CASE_SUPPORT",
            correlation_id="provider-unassigned",
        ),
        session,
    )
    foreign = await service.authorize(
        provider,
        "referral.read",
        AuthorizationContext.for_resource(
            "referral",
            data["foreign_referral_id"],
            purpose="CASE_SUPPORT",
            correlation_id="provider-foreign",
        ),
        session,
    )
    assert assigned.allowed
    assert not unrelated.allowed
    assert not foreign.allowed


async def test_persistent_scope_cannot_be_spoofed_by_request_context(security_data) -> None:
    _, session, data = security_data
    service = AuthorizationService()
    operator = _principal(data["operator"])

    spoofed_existing_read = await service.authorize(
        operator,
        "case.read.summary",
        _case_context(
            data["foreign_case_id"],
            intended_creation_scope=IntendedCreationScope(
                case_id=data["case_id"],
                organization_id=data["org_a"],
                jurisdiction_id=data["district_id"],
            ),
        ),
        session,
    )
    mismatched_type = await service.authorize(
        operator,
        "case.read.summary",
        AuthorizationContext.for_resource("referral", data["provider_referral_id"]),
        session,
    )

    assert not spoofed_existing_read.allowed
    assert spoofed_existing_read.reason_code == "UNTRUSTED_SCOPE_OVERRIDE"
    assert not mismatched_type.allowed
    assert mismatched_type.reason_code == "RESOURCE_TYPE_MISMATCH"


async def test_break_glass_is_scoped_and_expires(security_data) -> None:
    connection, session, data = security_data
    service = AuthorizationService()
    now = datetime.now(UTC)
    await connection.execute(
        text(
            "INSERT INTO access_elevations (actor_id, resource_type, resource_id, case_id, requested_permission, reason, policy_source, approved_by_actor_id, effective_from, expires_at, correlation_id) VALUES (:actor_id, 'transcript', :resource_id, :case_id, 'transcript.read', 'Synthetic incident', 'SECURITY_POLICY', :approver, :effective_from, :expires_at, 'break-glass-test')"
        ),
        {
            "actor_id": data["district"],
            "resource_id": str(data["transcript_id"]),
            "case_id": data["case_id"],
            "approver": data["approver"],
            "effective_from": now - timedelta(minutes=1),
            "expires_at": now + timedelta(minutes=5),
        },
    )
    decision = await service.authorize(
        _principal(data["district"]),
        "transcript.read",
        AuthorizationContext.for_resource(
            "transcript", data["transcript_id"], purpose="CASE_SUPPORT"
        ),
        session,
    )
    assert decision.allowed

    await connection.execute(
        text(
            "UPDATE access_elevations SET effective_from = now() - interval '2 minutes', expires_at = now() - interval '1 minute'"
        )
    )
    expired = await service.authorize(
        _principal(data["district"]),
        "transcript.read",
        AuthorizationContext.for_resource(
            "transcript", data["transcript_id"], purpose="CASE_SUPPORT"
        ),
        session,
    )
    assert not expired.allowed


async def test_identity_and_role_constraints_are_database_enforced(security_data) -> None:
    connection, _, data = security_data
    await connection.execute(
        text(
            "INSERT INTO actor_identities (actor_id, provider_code, issuer, subject) VALUES (:actor_id, 'test-oidc', 'https://issuer.test', 'duplicate-subject')"
        ),
        {"actor_id": data["operator"]},
    )
    with pytest.raises(IntegrityError):
        async with connection.begin_nested():
            await connection.execute(
                text(
                    "INSERT INTO actor_identities (actor_id, provider_code, issuer, subject) VALUES (:actor_id, 'test-oidc', 'https://issuer.test', 'duplicate-subject')"
                ),
                {"actor_id": data["provider"]},
            )

    role_id = await _id(connection, "SELECT id FROM roles WHERE code = 'AUDITOR'")
    with pytest.raises(IntegrityError):
        async with connection.begin_nested():
            await connection.execute(
                text(
                    "INSERT INTO actor_role_bindings (actor_id, role_id, granted_by_actor_id, reason, policy_version_id) VALUES (:actor_id, :role_id, :actor_id, 'self grant', :policy_id)"
                ),
                {"actor_id": data["operator"], "role_id": role_id, "policy_id": data["policy_id"]},
            )


async def test_active_break_glass_requires_independent_human_approver(security_data) -> None:
    connection, _, data = security_data
    statement = text(
        "INSERT INTO access_elevations (actor_id, resource_type, resource_id, case_id, requested_permission, reason, policy_source, approved_by_actor_id, expires_at, correlation_id) VALUES (:actor_id, 'transcript', :resource_id, :case_id, 'transcript.read', 'Synthetic incident', 'SECURITY_POLICY', :approver, now() + interval '5 minutes', :correlation_id)"
    )

    with pytest.raises(DBAPIError):
        async with connection.begin_nested():
            await connection.execute(
                statement,
                {
                    "actor_id": data["district"],
                    "resource_id": str(data["transcript_id"]),
                    "case_id": data["case_id"],
                    "approver": None,
                    "correlation_id": "missing-approver",
                },
            )

    with pytest.raises(DBAPIError):
        async with connection.begin_nested():
            await connection.execute(
                statement,
                {
                    "actor_id": data["district"],
                    "resource_id": str(data["transcript_id"]),
                    "case_id": data["case_id"],
                    "approver": data["system_admin"],
                    "correlation_id": "system-approver",
                },
            )


async def test_sensitive_fields_encrypt_on_orm_write_and_decrypt_only_after_authorization(
    security_data,
) -> None:
    connection, session, data = security_data
    old_key = b"1" * 32
    new_key = b"2" * 32

    class StaticProvider:
        def __init__(self, keys: dict[str, bytes], current: str) -> None:
            self.keys = keys
            self.current = current

        def current_key_id(self) -> str:
            return self.current

        def get_key(self, key_id: str) -> bytes:
            return self.keys[key_id]

    contact_plaintext = "+919876543210"
    transcript_plaintext = "highly sensitive transcript"
    translation_plaintext = "highly sensitive translation"
    writer = FieldEncryptor(StaticProvider({"KEY-V1": old_key}, "KEY-V1"))
    with use_field_encryptor(writer):
        contact = SubjectContact(
            subject_id=data["subject_id"],
            channel="PHONE",
            contact_value=contact_plaintext,
            is_primary=True,
            safe_to_use=False,
        )
        transcript = TranscriptSegment(
            interaction_id=data["interaction_id"],
            sequence=1,
            start_ms=101,
            end_ms=200,
            language="en",
            content=transcript_plaintext,
        )
        session.add_all([contact, transcript])
        await session.flush()
        translation = Translation(
            transcript_segment_id=transcript.id,
            target_language="hi",
            translated_content=translation_plaintext,
        )
        session.add(translation)
        await session.flush()
        contact_id = contact.id
        transcript_id = transcript.id
        translation_id = translation.id

    raw_values = (
        await connection.execute(
            text(
                "SELECT "
                "(SELECT contact_value FROM subject_contacts WHERE id = :contact_id), "
                "(SELECT content FROM transcript_segments WHERE id = :transcript_id), "
                "(SELECT translated_content FROM translations WHERE id = :translation_id)"
            ),
            {
                "contact_id": contact_id,
                "transcript_id": transcript_id,
                "translation_id": translation_id,
            },
        )
    ).one()
    for plaintext, stored in zip(
        (contact_plaintext, transcript_plaintext, translation_plaintext),
        raw_values,
        strict=True,
    ):
        assert plaintext not in str(stored)
        assert "KEY-V1" in str(stored)

    session.expunge_all()
    reader = FieldEncryptor(StaticProvider({"KEY-V1": old_key, "KEY-V2": new_key}, "KEY-V2"))
    with use_field_encryptor(reader):
        with pytest.raises((EncryptionError, StatementError)):
            await session.scalar(
                select(SubjectContact.contact_value).where(SubjectContact.id == contact_id)
            )

        access = SensitiveFieldAccessService()
        operator = _principal(data["operator"])
        with pytest.raises(AppException):
            await access.read_contact_value(
                operator,
                contact_id,
                AuthorizationContext.for_resource("contact", transcript_id, purpose="CASE_SUPPORT"),
                session,
            )
        assert (
            await access.read_contact_value(
                operator,
                contact_id,
                AuthorizationContext.for_resource("contact", contact_id, purpose="CASE_SUPPORT"),
                session,
            )
            == contact_plaintext
        )
        assert (
            await access.read_transcript_content(
                operator,
                transcript_id,
                AuthorizationContext.for_resource(
                    "transcript", transcript_id, purpose="CASE_SUPPORT"
                ),
                session,
            )
            == transcript_plaintext
        )
        assert (
            await access.read_translation_content(
                operator,
                translation_id,
                AuthorizationContext.for_resource(
                    "translation", translation_id, purpose="CASE_SUPPORT"
                ),
                session,
            )
            == translation_plaintext
        )

        auditor_contact = await AuthorizationService().authorize(
            _principal(data["auditor"], "AUDITOR"),
            "contact.read",
            AuthorizationContext.for_resource("contact", contact_id, purpose="CASE_SUPPORT"),
            session,
        )
        assert not auditor_contact.allowed

    actual_reads = await session.scalar(
        select(text("count(*)"))
        .select_from(AuditEvent)
        .where(
            AuditEvent.actor_id == data["operator"],
            AuditEvent.reason_code == "RESOURCE_READ",
        )
    )
    assert actual_reads == 3


def test_structured_logs_omit_tokens_and_sensitive_payloads() -> None:
    import logging

    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        "security",
        logging.INFO,
        __file__,
        1,
        "token=%s phone=%s",
        ("secret-token", "+919876543210"),
        None,
    )
    record.extra_fields = {
        "transcript": "raw transcript should never appear",
        "contact": "+919876543210",
        "safe_reason": "policy decision",
    }
    rendered = formatter.format(record)
    parsed = json.loads(rendered)
    assert "secret-token" not in rendered
    assert "+919876543210" not in rendered
    assert "raw transcript should never appear" not in rendered
    assert parsed["safe_reason"] == "policy decision"


@pytest.mark.anyio
async def test_protected_api_requires_authentication(client) -> None:
    response = await client.get("/api/v1/security/me")
    assert response.status_code == 401
    assert "token" not in response.text.lower()
