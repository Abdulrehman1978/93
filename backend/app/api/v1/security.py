"""Minimal protected endpoints proving backend PEP and DTO boundaries."""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.errors import AppException
from app.security.authorization import AuthorizationService
from app.security.context import AuthorizationContext
from app.security.dependencies import get_current_principal
from app.security.principal import SecurityPrincipal
from app.security.projections import CaseSummaryView, DataProjectionService, ProviderReferralView

router = APIRouter(prefix="/security", tags=["Security Foundation"])
authorization_service = AuthorizationService()
projection_service = DataProjectionService()
PrincipalDependency = Annotated[SecurityPrincipal, Depends(get_current_principal)]
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/me", response_model=dict[str, Any], summary="Authenticated principal summary")
async def principal_summary(
    principal: PrincipalDependency,
) -> dict[str, Any]:
    """Return only opaque principal metadata; no IdP profile claims are echoed."""
    return {
        "actor_id": str(principal.actor_id),
        "actor_type": principal.actor_type,
        "identity_provider": principal.identity_provider,
        "roles": list(principal.roles),
    }


@router.get("/cases/{case_id}/summary", response_model=CaseSummaryView)
async def case_summary(
    case_id: uuid.UUID,
    principal: PrincipalDependency,
    session: SessionDependency,
    purpose: Annotated[str | None, Header(alias="X-Processing-Purpose")] = None,
) -> CaseSummaryView:
    """Authorize before loading even the minimized case projection."""
    await authorization_service.authorize_or_raise(
        principal,
        "case.read.summary",
        AuthorizationContext.for_resource("case", case_id, purpose=purpose),
        session,
    )
    view = await projection_service.case_summary(session, case_id)
    if view is None:
        raise AppException(
            status_code=404, title="Not Found", detail="The requested resource is unavailable."
        )
    return view


@router.get("/referrals/{referral_id}/provider-view", response_model=ProviderReferralView)
async def provider_referral_view(
    referral_id: uuid.UUID,
    principal: PrincipalDependency,
    session: SessionDependency,
    purpose: Annotated[str | None, Header(alias="X-Processing-Purpose")] = None,
) -> ProviderReferralView:
    """Provider projection is scoped to the assigned referral only."""
    await authorization_service.authorize_or_raise(
        principal,
        "referral.read",
        AuthorizationContext.for_resource(
            "referral",
            referral_id,
            purpose=purpose,
            recipient="SERVICE_PROVIDER",
        ),
        session,
    )
    view = await projection_service.provider_referral(session, referral_id)
    if view is None:
        raise AppException(
            status_code=404, title="Not Found", detail="The requested resource is unavailable."
        )
    return view
