"""Anonymous session lifecycle with digest-only bearer credentials."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel.registry import ChannelType, InteractionMode, get_channel_capability
from app.channel.schemas import (
    ChannelSessionCreate,
    ChannelSessionResponse,
    ModeSelectionRequest,
    SessionControlResponse,
    SessionStateResponse,
)
from app.config import settings
from app.db.models.casework import Case, Interaction, InteractionEvent, Subject
from app.db.models.platform import AuditEvent
from app.errors import AppException
from app.privacy.processing_authorization import promote_interaction_authorizations_to_case


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _invalid_session() -> AppException:
    return AppException(
        status_code=401,
        title="Unauthorized",
        detail="Session credentials are invalid or unavailable.",
        type_uri="https://api.sambal.gov.in/errors/session-not-authorized",
    )


class ChannelSessionService:
    async def create(
        self, session: AsyncSession, request: ChannelSessionCreate
    ) -> ChannelSessionResponse:
        if request.channel is not ChannelType.WEB:
            raise AppException(
                status_code=409,
                title="Channel unavailable",
                detail="This channel is not available through the public gateway.",
                type_uri="https://api.sambal.gov.in/errors/channel-unavailable",
            )
        capability = get_channel_capability(request.channel)
        if request.interaction_mode not in capability.supported_modes:
            raise AppException(
                status_code=409,
                title="Interaction mode unavailable",
                detail="The requested interaction mode is not available for this channel.",
                type_uri="https://api.sambal.gov.in/errors/mode-unavailable",
            )
        if request.client_request_id:
            existing = await session.scalar(
                select(Interaction).where(
                    Interaction.channel == request.channel.value,
                    Interaction.external_reference == request.client_request_id,
                )
            )
            if existing is not None:
                raise AppException(
                    status_code=409,
                    title="Duplicate session request",
                    detail="The client request identifier has already been used.",
                    type_uri="https://api.sambal.gov.in/errors/idempotency-conflict",
                )

        now = datetime.now(UTC)
        raw_token = secrets.token_urlsafe(32)
        interaction_id = uuid.uuid4()
        subject = Subject(
            id=uuid.uuid4(),
            subject_reference=f"anon-session-{interaction_id.hex}",
            classification="PSEUDONYMIZED",
        )
        interaction = Interaction(
            id=interaction_id,
            subject_id=subject.id,
            case_id=None,
            channel=request.channel.value,
            interaction_mode=request.interaction_mode.value,
            status="OPEN",
            started_at=now,
            language=request.locale.lower(),
            external_reference=request.client_request_id,
            channel_metadata={
                "protocol_version": "packet-06-v1",
            },
            session_token_digest=token_digest(raw_token),
            session_expires_at=now + timedelta(seconds=settings.SESSION_TTL_SECONDS),
            last_activity_at=now,
            session_policy_version=settings.SESSION_POLICY_VERSION,
        )
        session.add(subject)
        await session.flush()
        session.add(interaction)
        session.add(
            InteractionEvent(
                interaction_id=interaction_id,
                event_type="SESSION_CREATED",
                occurred_at=now,
                source_reference=f"session:{interaction_id}",
                event_metadata={
                    "channel": request.channel.value,
                    "interaction_mode": request.interaction_mode.value,
                    "locale": request.locale.lower(),
                },
            )
        )
        session.add(
            AuditEvent(
                action="CHANNEL_SESSION_CREATED",
                entity_type="interaction",
                entity_id=str(interaction_id),
                purpose="PURP-01",
                safe_metadata={"channel": request.channel.value},
            )
        )
        await session.flush()
        assert interaction.session_expires_at is not None
        return ChannelSessionResponse(
            session_id=interaction_id,
            session_token=raw_token,
            expires_at=interaction.session_expires_at,
            channel=ChannelType.WEB,
            interaction_mode=InteractionMode(request.interaction_mode),
            policy_version=settings.SESSION_POLICY_VERSION,
            available_modes=capability.supported_modes,
        )

    async def authenticate(
        self, session: AsyncSession, session_id: uuid.UUID, raw_token: str, *, mutate: bool
    ) -> Interaction:
        if not raw_token or len(raw_token) > 512:
            raise _invalid_session()
        interaction = await session.scalar(
            select(Interaction).where(Interaction.id == session_id).with_for_update()
            if mutate
            else select(Interaction).where(Interaction.id == session_id)
        )
        if interaction is None or interaction.session_token_digest is None:
            raise _invalid_session()
        if not hmac.compare_digest(interaction.session_token_digest, token_digest(raw_token)):
            raise _invalid_session()
        now = datetime.now(UTC)
        if interaction.status != "OPEN" or self._expired(interaction, now):
            raise _invalid_session()
        if mutate:
            interaction.last_activity_at = now
        return interaction

    @staticmethod
    def _expired(interaction: Interaction, now: datetime) -> bool:
        if interaction.session_expires_at is None or interaction.last_activity_at is None:
            return True
        absolute_expiry = interaction.started_at + timedelta(
            seconds=settings.SESSION_ABSOLUTE_MAX_SECONDS
        )
        return (
            now >= interaction.session_expires_at
            or now >= absolute_expiry
            or now - interaction.last_activity_at
            >= timedelta(seconds=settings.SESSION_IDLE_TIMEOUT_SECONDS)
        )

    async def state(
        self, session: AsyncSession, session_id: uuid.UUID, raw_token: str
    ) -> SessionStateResponse:
        interaction = await self.authenticate(session, session_id, raw_token, mutate=False)
        return SessionStateResponse(
            session_id=interaction.id,
            channel=ChannelType(interaction.channel),
            interaction_mode=InteractionMode(interaction.interaction_mode),
            status=interaction.status,
            language=interaction.language,
            expires_at=interaction.session_expires_at,
            last_activity_at=interaction.last_activity_at,
            policy_version=interaction.session_policy_version,
        )

    async def select_mode(
        self,
        session: AsyncSession,
        session_id: uuid.UUID,
        raw_token: str,
        request: ModeSelectionRequest,
    ) -> SessionControlResponse:
        interaction = await self.authenticate(session, session_id, raw_token, mutate=True)
        capability = get_channel_capability(ChannelType(interaction.channel))
        if request.interaction_mode not in capability.supported_modes:
            raise AppException(
                409,
                "Interaction mode unavailable",
                "The requested interaction mode is not available for this channel.",
                "https://api.sambal.gov.in/errors/mode-unavailable",
            )
        now = datetime.now(UTC)
        interaction.interaction_mode = request.interaction_mode.value
        session.add(
            InteractionEvent(
                interaction_id=interaction.id,
                event_type="MODE_SELECTED",
                occurred_at=now,
                source_reference=f"mode:{request.interaction_mode.value}",
                event_metadata={"interaction_mode": request.interaction_mode.value},
            )
        )
        await session.flush()
        return SessionControlResponse(
            session_id=interaction.id,
            status=interaction.status,
            interaction_mode=InteractionMode(interaction.interaction_mode),
        )

    async def close(
        self, session: AsyncSession, session_id: uuid.UUID, raw_token: str, status: str
    ) -> SessionControlResponse:
        if status not in {"COMPLETED", "ABANDONED"}:
            raise ValueError(status)
        interaction = await self.authenticate(session, session_id, raw_token, mutate=True)
        now = datetime.now(UTC)
        interaction.status = status
        interaction.ended_at = now
        session.add(
            InteractionEvent(
                interaction_id=interaction.id,
                event_type=f"SESSION_{status}",
                occurred_at=now,
                source_reference=f"control:{status.lower()}",
                event_metadata={"status": status},
            )
        )
        session.add(
            AuditEvent(
                action=f"CHANNEL_SESSION_{status}",
                entity_type="interaction",
                entity_id=str(interaction.id),
                safe_metadata={"channel": interaction.channel, "status": status},
            )
        )
        await session.flush()
        return SessionControlResponse(
            session_id=interaction.id,
            status=status,
            interaction_mode=InteractionMode(interaction.interaction_mode),
        )

    async def bind_to_case(
        self,
        session: AsyncSession,
        session_id: uuid.UUID,
        raw_token: str,
        case_id: uuid.UUID,
    ) -> Interaction:
        interaction = await self.authenticate(session, session_id, raw_token, mutate=True)
        case = await session.scalar(select(Case).where(Case.id == case_id).with_for_update())
        if case is None or case.subject_id != interaction.subject_id:
            raise AppException(
                404,
                "Case unavailable",
                "The requested case is unavailable.",
                "https://api.sambal.gov.in/errors/case-unavailable",
            )
        if interaction.case_id is not None and interaction.case_id != case_id:
            raise AppException(
                409,
                "Interaction already bound",
                "The interaction is already bound to a different case.",
                "https://api.sambal.gov.in/errors/interaction-bound",
            )
        if interaction.case_id == case_id:
            return interaction
        interaction.case_id = case_id
        await promote_interaction_authorizations_to_case(session, interaction, case_id)
        session.add(
            InteractionEvent(
                interaction_id=interaction.id,
                event_type="CASE_BOUND",
                occurred_at=datetime.now(UTC),
                source_reference=f"case:{case_id}",
                event_metadata={"case_id": str(case_id)},
            )
        )
        session.add(
            AuditEvent(
                action="CHANNEL_SESSION_CASE_BOUND",
                entity_type="interaction",
                entity_id=str(interaction.id),
                safe_metadata={"case_id": str(case_id)},
            )
        )
        await session.flush()
        return interaction


channel_session_service = ChannelSessionService()
