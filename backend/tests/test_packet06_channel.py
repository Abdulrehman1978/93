"""Packet 06 channel-gateway and consent adversarial tests."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel.registry import (
    CapabilityStatus,
    ChannelType,
    InteractionMode,
    get_channel_capability,
)
from app.channel.schemas import (
    ChannelSessionCreate,
    ChannelSessionResponse,
    ConsentChoice,
    ConsentDecisionRequest,
    IntakeAcknowledgementRequest,
    SessionPolicyResponse,
)
from app.channel.session import ChannelSessionService, token_digest
from app.database import engine
from app.db.models.casework import Case, Interaction, InteractionEvent
from app.db.models.governance import PolicyVersion, ProcessingAuthorization
from app.db.models.platform import AuditEvent
from app.db.models.security import Actor, ActorRoleBinding, Role
from app.errors import AppException
from app.privacy.consent_engine import ConsentEngine
from app.security.principal import SecurityPrincipal


def test_channel_registry_reports_only_web_as_live_public_entrypoint() -> None:
    web = get_channel_capability(ChannelType.WEB)
    assert web.status is CapabilityStatus.LIVE_TESTED
    assert web.public_entrypoint is True
    assert web.supported_modes == (
        InteractionMode.UNSELECTED,
        InteractionMode.VOICE,
        InteractionMode.TEXT,
        InteractionMode.SILENT,
    )

    telephony = get_channel_capability(ChannelType.TELEPHONY)
    assert telephony.public_entrypoint is False
    assert telephony.status is CapabilityStatus.NOT_CONFIGURED


def test_session_tokens_are_digest_only() -> None:
    raw = "test-token-value"
    digest = token_digest(raw)
    assert digest != raw
    assert len(digest) == 64
    assert token_digest(raw) == digest


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


async def _new_session(
    session: AsyncSession,
    gateway: ChannelSessionService,
    *,
    mode: InteractionMode = InteractionMode.UNSELECTED,
) -> tuple[ChannelSessionResponse, Interaction]:
    created = await gateway.create(
        session,
        ChannelSessionCreate(
            interaction_mode=mode,
            client_request_id=f"packet06r2-{uuid.uuid4().hex[:12]}",
        ),
    )
    interaction = await session.get(Interaction, created.session_id)
    assert interaction is not None
    return created, interaction


async def _acknowledge(
    session: AsyncSession,
    consent: ConsentEngine,
    created: ChannelSessionResponse,
    interaction: Interaction,
) -> SessionPolicyResponse:
    policy = await consent.present_policy(session, interaction)
    await consent.acknowledge_intake(
        session,
        interaction.id,
        created.session_token,
        IntakeAcknowledgementRequest(
            policy_version=policy.policy_version,
            client_action_id=f"packet06r2-ack-{uuid.uuid4().hex[:12]}",
        ),
    )
    return policy


async def _new_case(session: AsyncSession, interaction: Interaction) -> Case:
    case = Case(
        id=uuid.uuid4(),
        public_tracking_id=f"PK06R2-{uuid.uuid4().hex[:16].upper()}",
        subject_id=interaction.subject_id,
    )
    session.add(case)
    await session.flush()
    return case


async def _supervisor(
    session: AsyncSession,
    *,
    actor_type: str = "STAFF",
    effective_to: datetime | None = None,
) -> tuple[Actor, SecurityPrincipal, ActorRoleBinding]:
    actor = Actor(
        id=uuid.uuid4(),
        actor_type=actor_type,
        display_reference=f"PK06R2-{uuid.uuid4().hex[:12]}",
        status="ACTIVE",
    )
    policy = await session.scalar(
        select(PolicyVersion).where(PolicyVersion.version_code == "packet-06-consent-v1")
    )
    role = await session.scalar(select(Role).where(Role.code == "SUPERVISOR"))
    assert policy is not None and role is not None
    binding = ActorRoleBinding(
        actor_id=actor.id,
        role_id=role.id,
        effective_from=datetime.now(UTC) - timedelta(minutes=1),
        effective_to=effective_to,
        reason="Packet 06R2 synthetic supervisor fixture",
        policy_version_id=policy.id,
    )
    session.add_all([actor, binding])
    await session.flush()
    principal = SecurityPrincipal(
        actor_id=actor.id,
        identity_provider="test-oidc",
        issuer="https://issuer.test",
        external_subject=f"pk06r2-{actor.id}",
        actor_type=actor_type,
        roles=("SUPERVISOR",),
    )
    return actor, principal, binding


@pytest.mark.integration
async def test_session_consent_is_append_only_and_idempotent() -> None:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        try:
            session = AsyncSession(bind=connection, expire_on_commit=False)
            gateway = ChannelSessionService()
            engine_service = ConsentEngine(gateway)
            created = await gateway.create(
                session,
                ChannelSessionCreate(locale="hi", client_request_id="packet06-test-request"),
            )
            interaction = await session.get(Interaction, created.session_id)
            assert interaction is not None
            assert interaction.session_token_digest == token_digest(created.session_token)
            assert created.session_token not in str(interaction.channel_metadata)
            assert (
                await session.scalar(
                    select(ProcessingAuthorization.id).where(
                        ProcessingAuthorization.interaction_id == created.session_id
                    )
                )
                is None
            )

            policy = await engine_service.present_policy(session, interaction)
            assert policy.served_locale == "en"
            assert policy.translation_status.value == "FALLBACK_LANGUAGE"
            assert any(item.purpose_code == "PURP-08" for item in policy.optional_consents)

            await engine_service.acknowledge_intake(
                session,
                created.session_id,
                created.session_token,
                IntakeAcknowledgementRequest(
                    policy_version=policy.policy_version,
                    client_action_id="packet06-intake-continue",
                ),
            )
            intake_auth = (
                await session.scalars(
                    select(ProcessingAuthorization).where(
                        ProcessingAuthorization.interaction_id == created.session_id
                    )
                )
            ).all()
            assert len(intake_auth) == 1

            grant = await engine_service.record(
                session,
                created.session_id,
                created.session_token,
                ConsentDecisionRequest(
                    purpose_code="PURP-08",
                    choice=ConsentChoice.GRANTED,
                    policy_version=policy.policy_version,
                    client_action_id="packet06-consent-1",
                ),
            )
            duplicate = await engine_service.record(
                session,
                created.session_id,
                created.session_token,
                ConsentDecisionRequest(
                    purpose_code="PURP-08",
                    choice=ConsentChoice.GRANTED,
                    policy_version=policy.policy_version,
                    client_action_id="packet06-consent-1",
                ),
            )
            assert grant.consent_event_id == duplicate.consent_event_id
            assert grant.current_processing_authorized is True
            second_grant = await engine_service.record(
                session,
                created.session_id,
                created.session_token,
                ConsentDecisionRequest(
                    purpose_code="PURP-08",
                    choice=ConsentChoice.GRANTED,
                    policy_version=policy.policy_version,
                    client_action_id="packet06-consent-1b",
                ),
            )
            assert second_grant.current_processing_authorized is True
            active_authorizations = (
                await session.scalars(
                    select(ProcessingAuthorization).where(
                        ProcessingAuthorization.interaction_id == created.session_id,
                        ProcessingAuthorization.status == "ACTIVE",
                    )
                )
            ).all()
            assert len(active_authorizations) == 2

            with pytest.raises(AppException) as conflict:
                await engine_service.record(
                    session,
                    created.session_id,
                    created.session_token,
                    ConsentDecisionRequest(
                        purpose_code="PURP-08",
                        choice=ConsentChoice.DECLINED,
                        policy_version=policy.policy_version,
                        client_action_id="packet06-consent-1",
                    ),
                )
            assert conflict.value.status_code == 409

            revoked = await engine_service.record(
                session,
                created.session_id,
                created.session_token,
                ConsentDecisionRequest(
                    purpose_code="PURP-08",
                    choice=ConsentChoice.REVOKED,
                    policy_version=policy.policy_version,
                    client_action_id="packet06-consent-2",
                ),
            )
            assert revoked.current_processing_authorized is False

            events = (
                await session.scalars(
                    select(InteractionEvent).where(
                        InteractionEvent.interaction_id == created.session_id
                    )
                )
            ).all()
            assert any(event.event_type == "NOTICE_PRESENTED" for event in events)
            assert all(created.session_token not in str(event.event_metadata) for event in events)
            audit = (
                await session.scalars(
                    select(AuditEvent).where(
                        AuditEvent.entity_type.in_({"interaction", "consent_event"})
                    )
                )
            ).all()
            assert all(created.session_token not in str(event.safe_metadata) for event in audit)
            authorizations = (
                await session.scalars(
                    select(ProcessingAuthorization).where(
                        ProcessingAuthorization.interaction_id == created.session_id
                    )
                )
            ).all()
            assert any(item.status == "REVOKED" for item in authorizations)
        finally:
            await transaction.rollback()
            await engine.dispose()
