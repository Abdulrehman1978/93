"""Canonical public channel gateway endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.privacy import apply_public_privacy_headers
from app.channel.registry import all_channel_capabilities
from app.channel.schemas import (
    ChannelCapabilityResponse,
    ChannelSessionCreate,
    ChannelSessionResponse,
    ConsentDecisionRequest,
    ConsentReceipt,
    IntakeAcknowledgementRequest,
    ModeSelectionRequest,
    SessionControlResponse,
    SessionPolicyResponse,
    SessionStateResponse,
)
from app.channel.session import channel_session_service
from app.database import get_db_session
from app.privacy.consent_engine import consent_engine

router = APIRouter(prefix="/channel", tags=["Channel Gateway"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
SessionToken = Annotated[str | None, Header(alias="X-Channel-Session-Token")]


@router.get("/capabilities", response_model=tuple[ChannelCapabilityResponse, ...])
async def capabilities() -> tuple[ChannelCapabilityResponse, ...]:
    return tuple(
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


@router.post(
    "/sessions",
    response_model=ChannelSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    request: ChannelSessionCreate, db: DbSession, http_response: Response
) -> ChannelSessionResponse:
    apply_public_privacy_headers(http_response)
    response = await channel_session_service.create(db, request)
    await db.commit()
    return response


@router.get("/sessions/{session_id}", response_model=SessionStateResponse)
async def get_session(
    session_id: uuid.UUID, db: DbSession, token: SessionToken, http_response: Response
) -> SessionStateResponse:
    apply_public_privacy_headers(http_response)
    return await channel_session_service.state(db, session_id, token or "")


@router.get("/sessions/{session_id}/policy", response_model=SessionPolicyResponse)
async def get_policy(
    session_id: uuid.UUID, db: DbSession, token: SessionToken, http_response: Response
) -> SessionPolicyResponse:
    apply_public_privacy_headers(http_response)
    interaction = await channel_session_service.authenticate(
        db, session_id, token or "", mutate=False
    )
    response = await consent_engine.present_policy(db, interaction)
    await db.commit()
    return response


@router.post("/sessions/{session_id}/consents", response_model=ConsentReceipt)
async def record_consent(
    session_id: uuid.UUID,
    request: ConsentDecisionRequest,
    db: DbSession,
    token: SessionToken,
    http_response: Response,
) -> ConsentReceipt:
    apply_public_privacy_headers(http_response)
    receipt = await consent_engine.record(db, session_id, token or "", request)
    await db.commit()
    return receipt


@router.post("/sessions/{session_id}/intake/continue", response_model=SessionControlResponse)
async def continue_intake(
    session_id: uuid.UUID,
    request: IntakeAcknowledgementRequest,
    db: DbSession,
    token: SessionToken,
    http_response: Response,
) -> SessionControlResponse:
    apply_public_privacy_headers(http_response)
    response = await consent_engine.acknowledge_intake(db, session_id, token or "", request)
    await db.commit()
    return response


@router.post("/sessions/{session_id}/mode", response_model=SessionControlResponse)
async def select_mode(
    session_id: uuid.UUID,
    request: ModeSelectionRequest,
    db: DbSession,
    token: SessionToken,
    http_response: Response,
) -> SessionControlResponse:
    apply_public_privacy_headers(http_response)
    response = await channel_session_service.select_mode(db, session_id, token or "", request)
    await db.commit()
    return response


@router.post("/sessions/{session_id}/complete", response_model=SessionControlResponse)
async def complete_session(
    session_id: uuid.UUID, db: DbSession, token: SessionToken, http_response: Response
) -> SessionControlResponse:
    apply_public_privacy_headers(http_response)
    response = await channel_session_service.close(db, session_id, token or "", "COMPLETED")
    await db.commit()
    return response


@router.post("/sessions/{session_id}/abandon", response_model=SessionControlResponse)
async def abandon_session(
    session_id: uuid.UUID, db: DbSession, token: SessionToken, http_response: Response
) -> SessionControlResponse:
    apply_public_privacy_headers(http_response)
    response = await channel_session_service.close(db, session_id, token or "", "ABANDONED")
    await db.commit()
    return response
