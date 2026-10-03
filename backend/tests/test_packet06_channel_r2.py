"""Packet 06R2 case-binding, conditional-consent, and trust-boundary tests."""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel.registry import InteractionMode
from app.channel.schemas import (
    ChannelSessionCreate,
    ConsentChoice,
    ConsentDecisionRequest,
    IntakeAcknowledgementRequest,
    ModeSelectionRequest,
)
from app.channel.session import ChannelSessionService
from app.database import engine
from app.db.models.casework import Case, InteractionEvent, Subject
from app.db.models.governance import (
    ConsentEvent,
    PolicyVersion,
    ProcessingAuthorityType,
    ProcessingAuthorization,
    ProcessingPurpose,
)
from app.db.models.platform import AuditEvent
from app.errors import AppException
from app.privacy.consent_engine import ConsentEngine
from app.privacy.policies import PACKET06_POLICY_HASH, ensure_packet06_catalog
from app.privacy.processing_authorization import create_interaction_authorization
from tests.test_packet06_channel import _acknowledge, _new_case, _new_session, _supervisor

pytestmark = pytest.mark.integration


@pytest.fixture
async def packet06_context() -> AsyncIterator[
    tuple[AsyncSession, ChannelSessionService, ConsentEngine]
]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            gateway = ChannelSessionService()
            yield session, gateway, ConsentEngine(gateway)
        finally:
            await session.close()
            await transaction.rollback()
            await engine.dispose()


async def _grant(
    session: AsyncSession,
    consent: ConsentEngine,
    created,
    purpose_code: str,
    policy_version: str,
    action: str | None = None,
) -> None:
    await consent.record(
        session,
        created.session_id,
        created.session_token,
        ConsentDecisionRequest(
            purpose_code=purpose_code,
            choice=ConsentChoice.GRANTED,
            policy_version=policy_version,
            client_action_id=action or f"packet06r2-grant-{uuid.uuid4().hex[:12]}",
        ),
    )


async def _voice_session(session, gateway, consent):
    created, interaction = await _new_session(session, gateway)
    interaction.interaction_mode = InteractionMode.VOICE.value
    await session.flush()
    policy = await _acknowledge(session, consent, created, interaction)
    return created, interaction, policy


async def test_case_binding_promotes_authorizations_without_collision(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction = await _new_session(session, gateway)
    policy = await _acknowledge(session, consent, created, interaction)
    await _grant(session, consent, created, "PURP-08", policy.policy_version)
    case = await _new_case(session, interaction)

    await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    authorizations = (
        await session.scalars(
            select(ProcessingAuthorization).where(
                ProcessingAuthorization.interaction_id == interaction.id
            )
        )
    ).all()
    interaction_scope = [item for item in authorizations if item.case_id is None]
    case_scope = [item for item in authorizations if item.case_id == case.id]
    assert len(interaction_scope) == 2
    assert len(case_scope) == 2
    assert {item.processing_purpose_id for item in interaction_scope} == {
        item.processing_purpose_id for item in case_scope
    }
    assert {item.authority_type_id for item in interaction_scope} == {
        item.authority_type_id for item in case_scope
    }
    assert all(
        item.policy_version_id == interaction_scope[0].policy_version_id for item in case_scope
    )
    assert any(item.consent_event_id is not None for item in case_scope)
    assert interaction.case_id == case.id
    assert await session.scalar(
        select(InteractionEvent.id).where(
            InteractionEvent.interaction_id == interaction.id,
            InteractionEvent.event_type == "CASE_BOUND",
        )
    )
    assert await session.scalar(
        select(AuditEvent.id).where(
            AuditEvent.entity_type == "interaction",
            AuditEvent.entity_id == str(interaction.id),
            AuditEvent.action == "CHANNEL_SESSION_CASE_BOUND",
        )
    )


async def test_case_binding_is_idempotent(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction = await _new_session(session, gateway)
    await _acknowledge(session, consent, created, interaction)
    case = await _new_case(session, interaction)
    await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    first_events = len(
        (
            await session.scalars(
                select(InteractionEvent).where(
                    InteractionEvent.interaction_id == interaction.id,
                    InteractionEvent.event_type == "CASE_BOUND",
                )
            )
        ).all()
    )
    first_audits = len(
        (
            await session.scalars(
                select(AuditEvent).where(
                    AuditEvent.entity_id == str(interaction.id),
                    AuditEvent.action == "CHANNEL_SESSION_CASE_BOUND",
                )
            )
        ).all()
    )
    await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    assert (
        len(
            (
                await session.scalars(
                    select(InteractionEvent).where(
                        InteractionEvent.interaction_id == interaction.id,
                        InteractionEvent.event_type == "CASE_BOUND",
                    )
                )
            ).all()
        )
        == first_events
    )
    assert (
        len(
            (
                await session.scalars(
                    select(AuditEvent).where(
                        AuditEvent.entity_id == str(interaction.id),
                        AuditEvent.action == "CHANNEL_SESSION_CASE_BOUND",
                    )
                )
            ).all()
        )
        == first_audits
    )


async def test_case_binding_rejects_foreign_case(packet06_context) -> None:
    session, gateway, _ = packet06_context
    created, interaction = await _new_session(session, gateway)
    foreign_subject_case = Case(
        id=uuid.uuid4(),
        public_tracking_id=f"PK06R2-{uuid.uuid4().hex[:16].upper()}",
        subject_id=uuid.uuid4(),
    )
    # The foreign subject must exist for the FK, but it must not be the session subject.
    subject = Subject(
        id=foreign_subject_case.subject_id,
        subject_reference=f"pk06r2-foreign-{uuid.uuid4().hex[:10]}",
        classification="PSEUDONYMIZED",
    )
    session.add(subject)
    await session.flush()
    session.add(foreign_subject_case)
    await session.flush()
    with pytest.raises(AppException) as exc:
        await gateway.bind_to_case(
            session, created.session_id, created.session_token, foreign_subject_case.id
        )
    assert exc.value.status_code == 404
    assert interaction.case_id is None


async def test_case_binding_rejects_different_second_case(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction = await _new_session(session, gateway)
    await _acknowledge(session, consent, created, interaction)
    first = await _new_case(session, interaction)
    second = await _new_case(session, interaction)
    await gateway.bind_to_case(session, created.session_id, created.session_token, first.id)
    with pytest.raises(AppException) as exc:
        await gateway.bind_to_case(session, created.session_id, created.session_token, second.id)
    assert exc.value.status_code == 409


async def test_case_binding_rejects_completed_and_abandoned_session(packet06_context) -> None:
    session, gateway, _ = packet06_context
    for status in ("COMPLETED", "ABANDONED"):
        created, interaction = await _new_session(session, gateway)
        case = await _new_case(session, interaction)
        await gateway.close(session, created.session_id, created.session_token, status)
        with pytest.raises(AppException) as exc:
            await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
        assert exc.value.status_code == 401


async def test_case_binding_rejects_expired_session(packet06_context) -> None:
    session, gateway, _ = packet06_context
    created, interaction = await _new_session(session, gateway)
    case = await _new_case(session, interaction)
    interaction.session_expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await session.flush()
    with pytest.raises(AppException) as exc:
        await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    assert exc.value.status_code == 401


async def test_text_policy_does_not_require_transcription(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction = await _new_session(session, gateway, mode=InteractionMode.TEXT)
    policy = await consent.present_policy(session, interaction)
    required = {item.purpose_code for item in policy.required_notices}
    assert "PURP-01" in required
    assert "PURP-02" not in required
    assert {item.purpose_code for item in policy.conditional_consents} == {"PURP-02"}


async def test_silent_policy_does_not_require_transcription(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction = await _new_session(session, gateway)
    interaction.interaction_mode = InteractionMode.SILENT.value
    await session.flush()
    policy = await consent.present_policy(session, interaction)
    assert "PURP-02" not in {item.purpose_code for item in policy.required_notices}


async def test_voice_policy_requires_transcription(packet06_context) -> None:
    session, gateway, consent = packet06_context
    _, _, policy = await _voice_session(session, gateway, consent)
    assert "PURP-02" in {item.purpose_code for item in policy.required_notices}
    assert "PURP-02" not in {item.purpose_code for item in policy.conditional_consents}


async def test_unselected_policy_defers_transcription_requirement(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction = await _new_session(session, gateway)
    policy = await consent.present_policy(session, interaction)
    assert "PURP-02" not in {item.purpose_code for item in policy.required_notices}
    assert "PURP-02" in {item.purpose_code for item in policy.conditional_consents}


async def test_consent_authority_cannot_be_fabricated_by_staff(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction, _ = await _voice_session(session, gateway, consent)
    case = await _new_case(session, interaction)
    await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    _, principal, _ = await _supervisor(session)
    with pytest.raises(AppException) as exc:
        await create_interaction_authorization(
            session,
            interaction,
            "PURP-06",
            actor=principal,
            lawful_authority="CONSENT",
        )
    assert exc.value.status_code == 403
    assert not await session.scalar(
        select(ProcessingAuthorization.id)
        .join(
            ProcessingPurpose, ProcessingPurpose.id == ProcessingAuthorization.processing_purpose_id
        )
        .where(
            ProcessingAuthorization.interaction_id == interaction.id,
            ProcessingAuthorization.case_id == case.id,
            ProcessingPurpose.purpose_code == "PURP-06",
        )
    )


async def test_database_rejects_consent_authorization_without_event(packet06_context) -> None:
    session, gateway, _ = packet06_context
    created, interaction = await _new_session(session, gateway)
    purpose = await session.scalar(
        select(ProcessingPurpose).where(ProcessingPurpose.purpose_code == "PURP-08")
    )
    authority = await session.scalar(
        select(ProcessingAuthorityType).where(ProcessingAuthorityType.authority_code == "CONSENT")
    )
    policy = await session.scalar(
        select(PolicyVersion).where(PolicyVersion.version_code == "packet-06-consent-v1")
    )
    assert purpose is not None and authority is not None and policy is not None
    with pytest.raises(DBAPIError):
        async with session.begin_nested():
            session.add(
                ProcessingAuthorization(
                    interaction_id=interaction.id,
                    processing_purpose_id=purpose.id,
                    authority_type_id=authority.id,
                    authorization_reason="Synthetic invalid consent provenance",
                    policy_version_id=policy.id,
                )
            )
            await session.flush()


async def test_legal_obligation_does_not_create_consent_event(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction, _ = await _voice_session(session, gateway, consent)
    case = await _new_case(session, interaction)
    await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    actor, principal, _ = await _supervisor(session)
    authorization = await create_interaction_authorization(
        session,
        interaction,
        "PURP-06",
        actor=principal,
        lawful_authority="LEGAL_OBLIGATION",
    )
    assert authorization.case_id == case.id
    assert authorization.interaction_id == interaction.id
    assert authorization.actor_id == actor.id
    assert authorization.consent_event_id is None
    assert await session.scalar(
        select(AuditEvent.id).where(
            AuditEvent.entity_type == "processing_authorization",
            AuditEvent.entity_id == str(authorization.id),
        )
    )


async def test_emergency_authorities_require_live_staff(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction, _ = await _voice_session(session, gateway, consent)
    case = await _new_case(session, interaction)
    await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    _, principal, _ = await _supervisor(session)
    for authority in ("MEDICAL_EMERGENCY", "PUBLIC_ORDER_OR_DISASTER_ASSISTANCE"):
        authorization = await create_interaction_authorization(
            session,
            interaction,
            "PURP-09",
            actor=principal,
            lawful_authority=authority,
        )
        assert authorization.actor_id == principal.actor_id
        assert authorization.consent_event_id is None


async def test_stale_supervisor_role_is_denied(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction, _ = await _voice_session(session, gateway, consent)
    case = await _new_case(session, interaction)
    await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    _, principal, binding = await _supervisor(session)
    binding.effective_to = datetime.now(UTC) - timedelta(seconds=1)
    await session.flush()
    with pytest.raises(AppException) as exc:
        await create_interaction_authorization(
            session,
            interaction,
            "PURP-06",
            actor=principal,
            lawful_authority="LEGAL_OBLIGATION",
        )
    assert exc.value.status_code == 403


@pytest.mark.parametrize("actor_type", ["AUDITOR", "SYSTEM", "SERVICE_PROVIDER", "CITIZEN"])
async def test_non_staff_authority_creation_is_denied(packet06_context, actor_type: str) -> None:
    session, gateway, consent = packet06_context
    created, interaction, _ = await _voice_session(session, gateway, consent)
    case = await _new_case(session, interaction)
    await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    _, principal, _ = await _supervisor(session, actor_type=actor_type)
    with pytest.raises(AppException) as exc:
        await create_interaction_authorization(
            session,
            interaction,
            "PURP-06",
            actor=principal,
            lawful_authority="LEGAL_OBLIGATION",
        )
    assert exc.value.status_code == 403


async def test_cross_session_token_is_denied(packet06_context) -> None:
    session, gateway, _ = packet06_context
    first, _ = await _new_session(session, gateway)
    second, _ = await _new_session(session, gateway)
    with pytest.raises(AppException) as exc:
        await gateway.state(session, second.session_id, first.session_token)
    assert exc.value.status_code == 401


async def test_bad_and_empty_session_tokens_are_denied(packet06_context) -> None:
    session, gateway, _ = packet06_context
    created, _ = await _new_session(session, gateway)
    for token in ("bad-token", ""):
        with pytest.raises(AppException) as exc:
            await gateway.state(session, created.session_id, token)
        assert exc.value.status_code == 401


async def test_expired_session_is_denied(packet06_context) -> None:
    session, gateway, _ = packet06_context
    created, interaction = await _new_session(session, gateway)
    interaction.session_expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await session.flush()
    with pytest.raises(AppException) as exc:
        await gateway.state(session, created.session_id, created.session_token)
    assert exc.value.status_code == 401


async def test_idle_and_absolute_session_limits_are_denied(packet06_context) -> None:
    session, gateway, _ = packet06_context
    created, interaction = await _new_session(session, gateway)
    interaction.last_activity_at = datetime.now(UTC) - timedelta(hours=1)
    await session.flush()
    with pytest.raises(AppException):
        await gateway.state(session, created.session_id, created.session_token)

    created, interaction = await _new_session(session, gateway)
    interaction.started_at = datetime.now(UTC) - timedelta(hours=2)
    await session.flush()
    with pytest.raises(AppException):
        await gateway.state(session, created.session_id, created.session_token)


async def test_closed_session_cannot_mutate(packet06_context) -> None:
    session, gateway, _ = packet06_context
    for status in ("COMPLETED", "ABANDONED"):
        created, _ = await _new_session(session, gateway)
        await gateway.close(session, created.session_id, created.session_token, status)
        with pytest.raises(AppException) as exc:
            await gateway.select_mode(
                session,
                created.session_id,
                created.session_token,
                request=ModeSelectionRequest(interaction_mode=InteractionMode.TEXT),
            )
        assert exc.value.status_code == 401


async def test_raw_token_is_absent_from_persistent_channel_records(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction = await _new_session(session, gateway)
    policy = await _acknowledge(session, consent, created, interaction)
    await _grant(session, consent, created, "PURP-08", policy.policy_version)
    raw = created.session_token
    values = [
        interaction.session_token_digest,
        str(interaction.channel_metadata),
        *[
            str(value)
            for value in (
                await session.scalars(
                    select(InteractionEvent.event_metadata).where(
                        InteractionEvent.interaction_id == interaction.id
                    )
                )
            ).all()
        ],
        *[
            str(value)
            for value in (
                await session.scalars(
                    select(AuditEvent.safe_metadata).where(
                        AuditEvent.entity_id.in_({str(interaction.id)})
                    )
                )
            ).all()
        ],
    ]
    assert raw not in " ".join(values)


async def test_session_logs_never_contain_raw_tokens(packet06_context, caplog) -> None:
    session, gateway, _ = packet06_context
    caplog.set_level(logging.INFO)
    created, interaction = await _new_session(session, gateway)
    await gateway.state(session, created.session_id, created.session_token)
    with pytest.raises(AppException):
        await gateway.state(session, created.session_id, "bad-token")
    interaction.session_expires_at = datetime.now(UTC) - timedelta(seconds=1)
    await session.flush()
    with pytest.raises(AppException):
        await gateway.state(session, created.session_id, created.session_token)
    assert created.session_token not in caplog.text


@pytest.mark.parametrize(
    "value",
    ["My phone number is 9876543210", "multi word prose", "line\nbreak", '{"token":"x"}', "x" * 81],
)
def test_client_identifiers_reject_narrative_and_structured_values(value: str) -> None:
    with pytest.raises(ValidationError):
        ChannelSessionCreate(client_request_id=value)
    with pytest.raises(ValidationError):
        ConsentDecisionRequest(
            purpose_code="PURP-08",
            choice=ConsentChoice.GRANTED,
            policy_version="packet-06-consent-v1",
            client_action_id=value,
        )


def test_client_identifiers_accept_opaque_values() -> None:
    for value in ("packet06-123", "550e8400-e29b-41d4-a716-446655440000", "client.request:123"):
        ChannelSessionCreate(client_request_id=value)
        ConsentDecisionRequest(
            purpose_code="PURP-08",
            choice=ConsentChoice.GRANTED,
            policy_version="packet-06-consent-v1",
            client_action_id=value,
        )


async def test_consent_rows_cannot_be_updated_or_deleted(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction = await _new_session(session, gateway)
    policy = await _acknowledge(session, consent, created, interaction)
    await _grant(session, consent, created, "PURP-08", policy.policy_version)
    event_id = await session.scalar(
        select(ConsentEvent.id).where(ConsentEvent.interaction_id == interaction.id)
    )
    assert event_id is not None
    with pytest.raises(DBAPIError):
        async with session.begin_nested():
            await session.execute(
                text("UPDATE consent_events SET reason = 'tampered' WHERE id = :event_id"),
                {"event_id": event_id},
            )
    with pytest.raises(DBAPIError):
        async with session.begin_nested():
            await session.execute(
                text("DELETE FROM consent_events WHERE id = :event_id"),
                {"event_id": event_id},
            )


async def test_stale_policy_and_notice_order_are_denied(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction = await _new_session(session, gateway)
    with pytest.raises(AppException) as exc:
        await consent.acknowledge_intake(
            session,
            created.session_id,
            created.session_token,
            IntakeAcknowledgementRequest(
                policy_version="previous-policy",
                client_action_id="packet06r2-stale-ack",
            ),
        )
    assert exc.value.status_code == 409
    with pytest.raises(AppException) as exc:
        await consent.acknowledge_intake(
            session,
            created.session_id,
            created.session_token,
            IntakeAcknowledgementRequest(
                policy_version="packet-06-consent-v1",
                client_action_id="packet06r2-no-notice",
            ),
        )
    assert exc.value.status_code == 409
    policy = await consent.present_policy(session, interaction)
    with pytest.raises(AppException) as exc:
        await consent.record(
            session,
            created.session_id,
            created.session_token,
            ConsentDecisionRequest(
                purpose_code="PURP-08",
                choice=ConsentChoice.GRANTED,
                policy_version="previous-policy",
                client_action_id="packet06r2-stale-consent",
            ),
        )
    assert exc.value.status_code == 409
    assert policy.policy_version == "packet-06-consent-v1"


async def test_purpose_isolation_and_dual_basis_revocation(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction, policy = await _voice_session(session, gateway, consent)
    await _grant(session, consent, created, "PURP-03", policy.policy_version)
    purposes = (
        await session.scalars(
            select(ProcessingPurpose.purpose_code)
            .join(
                ProcessingAuthorization,
                ProcessingAuthorization.processing_purpose_id == ProcessingPurpose.id,
            )
            .where(ProcessingAuthorization.interaction_id == interaction.id)
        )
    ).all()
    assert set(purposes) == {"PURP-01", "PURP-03"}

    await _grant(session, consent, created, "PURP-06", policy.policy_version)
    case = await _new_case(session, interaction)
    await gateway.bind_to_case(session, created.session_id, created.session_token, case.id)
    _, principal, _ = await _supervisor(session)
    legal = await create_interaction_authorization(
        session,
        interaction,
        "PURP-06",
        actor=principal,
        lawful_authority="LEGAL_OBLIGATION",
    )
    await consent.record(
        session,
        created.session_id,
        created.session_token,
        ConsentDecisionRequest(
            purpose_code="PURP-06",
            choice=ConsentChoice.REVOKED,
            policy_version=policy.policy_version,
            client_action_id="packet06r2-revoke-audio",
        ),
    )
    active = (
        await session.scalars(
            select(ProcessingAuthorization).where(
                ProcessingAuthorization.interaction_id == interaction.id,
                ProcessingAuthorization.processing_purpose_id == legal.processing_purpose_id,
                ProcessingAuthorization.status == "ACTIVE",
            )
        )
    ).all()
    assert len(active) == 1
    assert active[0].authority_type_id == legal.authority_type_id
    assert active[0].consent_event_id is None


async def test_regrant_preserves_lineage_and_one_active_authority(packet06_context) -> None:
    session, gateway, consent = packet06_context
    created, interaction, policy = await _voice_session(session, gateway, consent)
    await _grant(session, consent, created, "PURP-08", policy.policy_version, "packet06r2-g1")
    await consent.record(
        session,
        created.session_id,
        created.session_token,
        ConsentDecisionRequest(
            purpose_code="PURP-08",
            choice=ConsentChoice.REVOKED,
            policy_version=policy.policy_version,
            client_action_id="packet06r2-r1",
        ),
    )
    await _grant(session, consent, created, "PURP-08", policy.policy_version, "packet06r2-g2")
    events = (
        await session.scalars(
            select(ConsentEvent)
            .join(ProcessingPurpose, ProcessingPurpose.id == ConsentEvent.purpose_id)
            .where(
                ConsentEvent.interaction_id == interaction.id,
                ProcessingPurpose.purpose_code == "PURP-08",
            )
            .order_by(ConsentEvent.occurred_at, ConsentEvent.id)
        )
    ).all()
    assert [event.choice for event in events] == ["GRANTED", "REVOKED", "GRANTED"]
    assert events[1].previous_event_id == events[0].id
    assert events[2].previous_event_id == events[1].id
    assert (
        len(
            (
                await session.scalars(
                    select(ProcessingAuthorization)
                    .join(
                        ProcessingPurpose,
                        ProcessingPurpose.id == ProcessingAuthorization.processing_purpose_id,
                    )
                    .where(
                        ProcessingAuthorization.interaction_id == interaction.id,
                        ProcessingAuthorization.status == "ACTIVE",
                        ProcessingPurpose.purpose_code == "PURP-08",
                    )
                )
            ).all()
        )
        == 1
    )


async def test_policy_catalog_fails_closed_on_drift(packet06_context) -> None:
    session, _, _ = packet06_context
    policy = await session.scalar(
        select(PolicyVersion).where(PolicyVersion.version_code == "packet-06-consent-v1")
    )
    assert policy is not None
    policy.content_hash = "0" * 64
    await session.flush()
    with pytest.raises(AppException) as exc:
        await ensure_packet06_catalog(session)
    assert exc.value.status_code == 503


async def test_reference_catalog_contains_packet06r2_rows(packet06_context) -> None:
    session, _, _ = packet06_context
    policy = await ensure_packet06_catalog(session)
    assert policy.content_hash == PACKET06_POLICY_HASH
    purposes = set(
        await session.scalars(
            select(ProcessingPurpose.purpose_code).where(
                ProcessingPurpose.policy_version_id == policy.id
            )
        )
    )
    assert {"PURP-01", "PURP-02", "PURP-03", "PURP-06", "PURP-08", "PURP-09", "PURP-16"} <= purposes
    authorities = set(
        await session.scalars(
            select(ProcessingAuthorityType.authority_code).where(
                ProcessingAuthorityType.status == "ACTIVE"
            )
        )
    )
    assert {
        "CONSENT",
        "LEGAL_OBLIGATION",
        "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE",
        "MEDICAL_EMERGENCY",
        "PUBLIC_ORDER_OR_DISASTER_ASSISTANCE",
    } <= authorities
