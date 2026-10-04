"""Central, append-only, interaction-scoped consent state machine."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel.registry import InteractionMode, all_channel_capabilities
from app.channel.schemas import (
    ChannelCapabilityResponse,
    ConsentChoice,
    ConsentDecisionRequest,
    ConsentReceipt,
    IntakeAcknowledgementRequest,
    SessionControlResponse,
    SessionPolicyResponse,
    TranslationTruthStatus,
)
from app.channel.session import ChannelSessionService
from app.db.models.casework import Interaction, InteractionEvent
from app.db.models.governance import (
    ConsentEvent,
    ProcessingAuthorityType,
    ProcessingAuthorization,
    ProcessingPurpose,
)
from app.db.models.platform import AuditEvent
from app.errors import AppException
from app.privacy.policies import (
    PACKET06_POLICY_VERSION,
    PURPOSE_POLICIES,
    ensure_packet06_catalog,
    resolve_purpose,
)
from app.privacy.processing_authorization import create_interaction_authorization


def _translation(locale: str | None) -> tuple[str, TranslationTruthStatus]:
    normalized = (locale or "en").lower()
    if normalized == "en":
        return "en", TranslationTruthStatus.AUTHORITATIVE
    return "en", TranslationTruthStatus.FALLBACK_LANGUAGE


async def has_active_intake_authorization(session: AsyncSession, interaction_id: uuid.UUID) -> bool:
    authorization = await session.scalar(
        select(ProcessingAuthorization.id)
        .join(
            ProcessingPurpose,
            ProcessingPurpose.id == ProcessingAuthorization.processing_purpose_id,
        )
        .join(
            ProcessingAuthorityType,
            ProcessingAuthorityType.id == ProcessingAuthorization.authority_type_id,
        )
        .where(
            ProcessingAuthorization.interaction_id == interaction_id,
            ProcessingPurpose.purpose_code == "PURP-01",
            ProcessingAuthorityType.authority_code == "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE",
            ProcessingAuthorization.status == "ACTIVE",
        )
    )
    return authorization is not None


class ConsentEngine:
    def __init__(self, sessions: ChannelSessionService) -> None:
        self.sessions = sessions

    async def present_policy(
        self, session: AsyncSession, interaction: Interaction
    ) -> SessionPolicyResponse:
        policy = await ensure_packet06_catalog(session)
        served_locale, translation_status = _translation(interaction.language)
        for item in PURPOSE_POLICIES:
            if not item.notice_required:
                continue
            source_reference = f"notice:{item.code}:{policy.version_code}"
            existing = await session.scalar(
                select(InteractionEvent).where(
                    InteractionEvent.interaction_id == interaction.id,
                    InteractionEvent.source_reference == source_reference,
                )
            )
            if existing is None:
                session.add(
                    InteractionEvent(
                        interaction_id=interaction.id,
                        event_type="NOTICE_PRESENTED",
                        occurred_at=datetime.now(UTC),
                        source_reference=source_reference,
                        event_metadata={
                            "purpose_code": item.code,
                            "policy_version": policy.version_code,
                            "served_locale": served_locale,
                            "translation_status": translation_status.value,
                        },
                    )
                )
        current = await self._current_decisions(session, interaction.id)
        intake_ready = await has_active_intake_authorization(session, interaction.id)
        await session.flush()
        mode = InteractionMode(interaction.interaction_mode)
        applicable = tuple(item for item in PURPOSE_POLICIES if mode in item.applicable_modes)
        required = tuple(
            item.as_requirement()
            for item in applicable
            if item.consent_mode.value in {"REQUIRED", "NOT_REQUIRED"}
        )
        optional = tuple(
            item.as_requirement()
            for item in applicable
            if item.consent_mode.value in {"OPTIONAL", "PROHIBITED_WITHOUT_HUMAN_AUTHORIZATION"}
        )
        conditional = tuple(
            item.as_requirement()
            for item in PURPOSE_POLICIES
            if item.code == "PURP-02" and mode is not InteractionMode.VOICE
        )
        capabilities = tuple(
            ChannelCapabilityResponse(
                channel=item.channel,
                status=item.status,
                supported_modes=item.supported_modes,
                provider_code=item.provider_code,
                public_entrypoint=item.public_entrypoint,
                human_review_required=item.human_review_required,
                note=item.note,
            )
            for item in all_channel_capabilities()
        )
        return SessionPolicyResponse(
            policy_version=policy.version_code,
            requested_locale=interaction.language or "en",
            served_locale=served_locale,
            translation_status=translation_status,
            required_notices=required,
            optional_consents=optional,
            available_alternatives=("TEXT", "NO_AUDIO", "NO_EXTERNAL_PROVIDER"),
            current_decisions=current,
            capabilities=capabilities,
            conditional_consents=conditional,
            intake_ready=intake_ready,
        )

    async def record(
        self,
        session: AsyncSession,
        session_id: uuid.UUID,
        raw_token: str,
        request: ConsentDecisionRequest,
    ) -> ConsentReceipt:
        interaction = await self.sessions.authenticate(session, session_id, raw_token, mutate=True)
        policy = await ensure_packet06_catalog(session)
        if request.policy_version != policy.version_code:
            raise AppException(
                409,
                "Policy version stale",
                "The consent policy has changed; reload the policy before deciding.",
                "https://api.sambal.gov.in/errors/policy-version-stale",
            )
        try:
            purpose_policy = resolve_purpose(request.purpose_code)
        except KeyError as exc:
            raise AppException(
                404,
                "Purpose unavailable",
                "The requested processing purpose is unavailable.",
                "https://api.sambal.gov.in/errors/purpose-unavailable",
            ) from exc
        if purpose_policy.consent_mode.value not in {"REQUIRED", "OPTIONAL"}:
            raise AppException(
                409,
                "Consent not applicable",
                "This purpose cannot be authorized through anonymous consent.",
                "https://api.sambal.gov.in/errors/consent-not-applicable",
            )
        if request.purpose_code == "PURP-02" and interaction.interaction_mode != "VOICE":
            raise AppException(
                409,
                "Voice mode required",
                "Speech transcription requires an intentional voice interaction.",
                "https://api.sambal.gov.in/errors/voice-mode-required",
            )
        purpose = await session.scalar(
            select(ProcessingPurpose).where(ProcessingPurpose.purpose_code == request.purpose_code)
        )
        if purpose is None:
            raise AppException(
                503,
                "Policy unavailable",
                "The processing policy is not configured.",
                "https://api.sambal.gov.in/errors/policy-unavailable",
            )
        notice = await session.scalar(
            select(InteractionEvent).where(
                InteractionEvent.interaction_id == interaction.id,
                InteractionEvent.event_type == "NOTICE_PRESENTED",
                InteractionEvent.source_reference
                == f"notice:{request.purpose_code}:{policy.version_code}",
            )
        )
        if purpose_policy.notice_required and notice is None:
            raise AppException(
                409,
                "Notice required",
                "The applicable notice must be presented before consent is recorded.",
                "https://api.sambal.gov.in/errors/notice-required",
            )

        existing_action = await session.scalar(
            select(ConsentEvent).where(
                ConsentEvent.interaction_id == interaction.id,
                ConsentEvent.action_id == request.client_action_id,
            )
        )
        if existing_action is not None:
            if (
                existing_action.choice != request.choice.value
                or existing_action.purpose_id != purpose.id
            ):
                raise AppException(
                    409,
                    "Idempotency conflict",
                    "The client action identifier was reused for a different decision.",
                    "https://api.sambal.gov.in/errors/idempotency-conflict",
                )
            return await self._receipt(session, existing_action, request.purpose_code)

        latest = await session.scalar(
            select(ConsentEvent)
            .where(
                ConsentEvent.interaction_id == interaction.id,
                ConsentEvent.purpose_id == purpose.id,
            )
            .order_by(ConsentEvent.occurred_at.desc(), ConsentEvent.id.desc())
            .with_for_update()
        )
        if request.choice is ConsentChoice.REVOKED and (
            latest is None or latest.choice != "GRANTED"
        ):
            raise AppException(
                409,
                "Invalid consent transition",
                "Consent can only be revoked after it has been granted.",
                "https://api.sambal.gov.in/errors/invalid-consent-transition",
            )
        served_locale, translation_status = _translation(interaction.language)
        event = ConsentEvent(
            id=uuid.uuid4(),
            subject_id=interaction.subject_id,
            interaction_id=interaction.id,
            case_id=interaction.case_id,
            purpose_id=purpose.id,
            choice=request.choice.value,
            policy_version_id=policy.id,
            channel=interaction.channel,
            action_id=request.client_action_id,
            served_locale=served_locale,
            translation_status=translation_status.value,
            occurred_at=datetime.now(UTC),
            previous_event_id=latest.id if latest else None,
            reason="Person decision recorded through canonical channel gateway.",
        )
        session.add(event)
        if request.choice is ConsentChoice.GRANTED:
            authority = await session.scalar(
                select(ProcessingAuthorityType).where(
                    ProcessingAuthorityType.authority_code == "CONSENT"
                )
            )
            if authority is None:
                raise AppException(
                    503,
                    "Policy unavailable",
                    "The consent authority is not configured.",
                    "https://api.sambal.gov.in/errors/policy-unavailable",
                )
            active_consent = await session.scalar(
                select(ProcessingAuthorization.id)
                .join(
                    ProcessingAuthorityType,
                    ProcessingAuthorityType.id == ProcessingAuthorization.authority_type_id,
                )
                .where(
                    ProcessingAuthorization.interaction_id == interaction.id,
                    ProcessingAuthorization.processing_purpose_id == purpose.id,
                    ProcessingAuthorization.status == "ACTIVE",
                    ProcessingAuthorityType.authority_code == "CONSENT",
                )
                .with_for_update()
            )
            if active_consent is None:
                session.add(
                    ProcessingAuthorization(
                        interaction_id=interaction.id,
                        case_id=interaction.case_id,
                        processing_purpose_id=purpose.id,
                        authority_type_id=authority.id,
                        consent_event_id=event.id,
                        authorization_reason="Purpose-specific consent recorded in the append-only ledger.",
                        policy_version_id=policy.id,
                    )
                )
        elif request.choice is ConsentChoice.REVOKED:
            active = (
                await session.scalars(
                    select(ProcessingAuthorization)
                    .where(
                        ProcessingAuthorization.interaction_id == interaction.id,
                        ProcessingAuthorization.processing_purpose_id == purpose.id,
                        ProcessingAuthorization.status == "ACTIVE",
                        ProcessingAuthorization.authority_type_id == ProcessingAuthorityType.id,
                        ProcessingAuthorityType.authority_code == "CONSENT",
                    )
                    .with_for_update()
                )
            ).all()
            for authorization in active:
                authorization.status = "REVOKED"
                authorization.revoked_at = event.occurred_at
        session.add(
            InteractionEvent(
                interaction_id=interaction.id,
                event_type="CONSENT_RECORDED"
                if request.choice is not ConsentChoice.REVOKED
                else "CONSENT_REVOKED",
                occurred_at=event.occurred_at,
                source_reference=f"consent:{request.client_action_id}",
                event_metadata={
                    "purpose_code": request.purpose_code,
                    "choice": request.choice.value,
                    "policy_version": policy.version_code,
                    "served_locale": served_locale,
                    "translation_status": translation_status.value,
                },
            )
        )
        session.add(
            AuditEvent(
                action="CONSENT_DECISION_RECORDED",
                entity_type="consent_event",
                entity_id=str(event.id),
                purpose=request.purpose_code,
                policy_version_id=policy.id,
                safe_metadata={"choice": request.choice.value, "channel": interaction.channel},
            )
        )
        await session.flush()
        return await self._receipt(session, event, request.purpose_code)

    async def acknowledge_intake(
        self,
        session: AsyncSession,
        session_id: uuid.UUID,
        raw_token: str,
        request: IntakeAcknowledgementRequest,
    ) -> SessionControlResponse:
        interaction = await self.sessions.authenticate(session, session_id, raw_token, mutate=True)
        policy = await ensure_packet06_catalog(session)
        if request.policy_version != policy.version_code:
            raise AppException(
                409,
                "Policy version stale",
                "Reload the current notice before continuing.",
                "https://api.sambal.gov.in/errors/policy-version-stale",
            )
        source = f"intake-continue:{request.client_action_id}"
        existing = await session.scalar(
            select(InteractionEvent).where(
                InteractionEvent.interaction_id == interaction.id,
                InteractionEvent.source_reference == source,
            )
        )
        if existing is None:
            notice = await session.scalar(
                select(InteractionEvent).where(
                    InteractionEvent.interaction_id == interaction.id,
                    InteractionEvent.event_type == "NOTICE_PRESENTED",
                    InteractionEvent.source_reference == f"notice:PURP-01:{policy.version_code}",
                )
            )
            if notice is None:
                raise AppException(
                    409,
                    "Notice required",
                    "The intake notice must be presented before continuing.",
                    "https://api.sambal.gov.in/errors/notice-required",
                )
            now = datetime.now(UTC)
            session.add(
                InteractionEvent(
                    interaction_id=interaction.id,
                    event_type="INTAKE_CONTINUE_CONFIRMED",
                    occurred_at=now,
                    source_reference=source,
                    event_metadata={
                        "purpose_code": "PURP-01",
                        "policy_version": policy.version_code,
                    },
                )
            )
            existing_auth = await session.scalar(
                select(ProcessingAuthorization.id)
                .join(
                    ProcessingAuthorityType,
                    ProcessingAuthorityType.id == ProcessingAuthorization.authority_type_id,
                )
                .join(
                    ProcessingPurpose,
                    ProcessingPurpose.id == ProcessingAuthorization.processing_purpose_id,
                )
                .where(
                    ProcessingAuthorization.interaction_id == interaction.id,
                    ProcessingPurpose.purpose_code == "PURP-01",
                    ProcessingAuthorityType.authority_code
                    == "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE",
                    ProcessingAuthorization.status == "ACTIVE",
                )
            )
            if existing_auth is None:
                await create_interaction_authorization(session, interaction, "PURP-01")
            session.add(
                AuditEvent(
                    action="INTAKE_CONTINUE_CONFIRMED",
                    entity_type="interaction",
                    entity_id=str(interaction.id),
                    purpose="PURP-01",
                    policy_version_id=policy.id,
                    safe_metadata={"client_action_id": request.client_action_id},
                )
            )
            await session.flush()
        return SessionControlResponse(
            session_id=interaction.id,
            status=interaction.status,
            interaction_mode=InteractionMode(interaction.interaction_mode),
        )

    async def _current_decisions(
        self, session: AsyncSession, interaction_id: uuid.UUID
    ) -> dict[str, ConsentChoice]:
        events = (
            await session.scalars(
                select(ConsentEvent)
                .where(ConsentEvent.interaction_id == interaction_id)
                .order_by(ConsentEvent.occurred_at.asc(), ConsentEvent.id.asc())
            )
        ).all()
        decisions: dict[str, ConsentChoice] = {}
        purpose_rows = (
            await session.scalars(
                select(ProcessingPurpose).where(ProcessingPurpose.is_active.is_(True))
            )
        ).all()
        purpose_by_id = {row.id: row.purpose_code for row in purpose_rows}
        for event in events:
            if event.choice in {"GRANTED", "DECLINED", "REVOKED"}:
                decisions[purpose_by_id[event.purpose_id]] = ConsentChoice(event.choice)
        return decisions

    async def _receipt(
        self, session: AsyncSession, event: ConsentEvent, purpose_code: str
    ) -> ConsentReceipt:
        authorized = False
        if event.choice == "GRANTED":
            authorized = (
                await session.scalar(
                    select(ProcessingAuthorization.id)
                    .join(
                        ProcessingAuthorityType,
                        ProcessingAuthorityType.id == ProcessingAuthorization.authority_type_id,
                    )
                    .where(
                        ProcessingAuthorization.interaction_id == event.interaction_id,
                        ProcessingAuthorization.processing_purpose_id == event.purpose_id,
                        ProcessingAuthorization.status == "ACTIVE",
                        ProcessingAuthorityType.authority_code == "CONSENT",
                    )
                )
            ) is not None
        return ConsentReceipt(
            consent_event_id=event.id,
            purpose_code=purpose_code,
            choice=ConsentChoice(event.choice),
            policy_version=PACKET06_POLICY_VERSION,
            recorded_at=event.occurred_at,
            current_processing_authorized=authorized,
        )


consent_engine = ConsentEngine(ChannelSessionService())
