"""Single FastAPI authentication extraction dependency for protected operations."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.errors import AppException
from app.security.authorization import AuthorizationService
from app.security.identity import TokenValidationError, provider_from_settings
from app.security.principal import SecurityPrincipal

authorization_service = AuthorizationService()


async def get_current_principal(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> SecurityPrincipal:
    """Authenticate one bearer token and map it to active local actor state."""
    if not authorization or not authorization.startswith("Bearer "):
        raise AppException(
            status_code=401,
            title="Unauthorized",
            detail="Authentication is required.",
            type_uri="https://api.sambal.gov.in/errors/authentication-required",
        )
    provider = provider_from_settings()
    if provider is None:
        raise AppException(
            status_code=401,
            title="Unauthorized",
            detail="Authentication is not configured for this deployment.",
            type_uri="https://api.sambal.gov.in/errors/authentication-unavailable",
        )
    try:
        token = await provider.validate_token(authorization.removeprefix("Bearer ").strip())
        resolved = await provider.resolve_identity(token, session)
    except TokenValidationError as exc:
        raise AppException(
            status_code=401,
            title="Unauthorized",
            detail="The access token could not be validated.",
            type_uri="https://api.sambal.gov.in/errors/invalid-token",
        ) from exc
    if resolved is None:
        raise AppException(
            status_code=401,
            title="Unauthorized",
            detail="The authenticated identity is not active in this application.",
            type_uri="https://api.sambal.gov.in/errors/identity-not-mapped",
        )
    return await authorization_service.load_principal(
        resolved.actor,
        provider_code=token.provider_code,
        issuer=token.issuer,
        external_subject=token.subject,
        authentication_context={
            key: token.claims[key]
            for key in ("acr", "amr")
            if key in token.claims and isinstance(token.claims[key], (str, list))
        },
        session=session,
    )
