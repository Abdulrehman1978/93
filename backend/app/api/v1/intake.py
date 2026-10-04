"""Citizen Write and Silent intake endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.privacy import apply_public_privacy_headers
from app.database import get_db_session
from app.intake.schemas import (
    IntakeSubmissionResponse,
    SilentIntakeRequest,
    WriteIntakeRequest,
)
from app.intake.service import CitizenIntakeService

router = APIRouter(prefix="/intake", tags=["Citizen Intake"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
SessionToken = Annotated[str | None, Header(alias="X-Channel-Session-Token")]
intake_service = CitizenIntakeService()


@router.post(
    "/sessions/{session_id}/write",
    response_model=IntakeSubmissionResponse,
    status_code=201,
)
async def submit_write(
    session_id: uuid.UUID,
    request: WriteIntakeRequest,
    db: DbSession,
    token: SessionToken,
    response: Response,
) -> IntakeSubmissionResponse:
    apply_public_privacy_headers(response)
    result = await intake_service.submit_write(db, session_id, token or "", request)
    await db.commit()
    if not result.case_created:
        response.status_code = 200
    return result


@router.post(
    "/sessions/{session_id}/silent",
    response_model=IntakeSubmissionResponse,
    status_code=201,
)
async def submit_silent(
    session_id: uuid.UUID,
    request: SilentIntakeRequest,
    db: DbSession,
    token: SessionToken,
    response: Response,
) -> IntakeSubmissionResponse:
    apply_public_privacy_headers(response)
    result = await intake_service.submit_silent(db, session_id, token or "", request)
    await db.commit()
    if not result.case_created:
        response.status_code = 200
    return result
