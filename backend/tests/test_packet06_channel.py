"""Packet 06 channel-gateway and consent adversarial tests."""

from __future__ import annotations

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
    ConsentChoice,
    ConsentDecisionRequest,
    IntakeAcknowledgementRequest,
)
from app.channel.session import ChannelSessionService, token_digest
from app.database import engine
from app.db.models.casework import Interaction, InteractionEvent
from app.db.models.governance import ProcessingAuthorization
from app.db.models.platform import AuditEvent
from app.errors import AppException
from app.privacy.consent_engine import ConsentEngine


def test_channel_registry_reports_only_web_as_live_public_entrypoint() -> None:
    web = get_channel_capability(ChannelType.WEB)
    assert web.status is CapabilityStatus.LIVE_TESTED
    assert web.public_entrypoint is True
    assert web.supported_modes == (InteractionMode.UNSELECTED, InteractionMode.TEXT)

    telephony = get_channel_capability(ChannelType.TELEPHONY)
    assert telephony.public_entrypoint is False
    assert telephony.status is CapabilityStatus.NOT_CONFIGURED


def test_session_tokens_are_digest_only() -> None:
    raw = "test-token-value"
    digest = token_digest(raw)
    assert digest != raw
    assert len(digest) == 64
    assert token_digest(raw) == digest


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
