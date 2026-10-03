"""Provider-neutral OIDC/OAuth token validation and local identity resolution."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
import jwt
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import Actor, ActorIdentity


class TokenValidationError(Exception):
    """Raised for any token failure without revealing verification internals."""


@dataclass(frozen=True, slots=True)
class ValidatedToken:
    issuer: str
    subject: str
    claims: dict[str, Any]
    provider_code: str


class IdentityProvider(Protocol):
    """Stable application boundary implemented by OIDC-compatible providers."""

    async def validate_token(self, token: str) -> ValidatedToken: ...

    async def resolve_identity(
        self, token: ValidatedToken, session: AsyncSession
    ) -> ResolvedIdentity | None: ...

    def provider_metadata(self) -> dict[str, str | bool]: ...


@dataclass(frozen=True, slots=True)
class ResolvedIdentity:
    actor: Actor
    identity: ActorIdentity


class OIDCIdentityProvider:
    """Small fail-closed OIDC verifier with bounded JWKS caching."""

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        jwks_uri: str,
        provider_code: str,
        algorithms: list[str],
        clock_skew_seconds: int = 30,
        cache_seconds: int = 300,
        jwks_loader: Callable[[], Awaitable[dict[str, Any]]] | None = None,
    ) -> None:
        if not issuer or not audience or not jwks_uri:
            raise ValueError("OIDC issuer, audience, and JWKS URI are required")
        if not algorithms:
            raise ValueError("At least one approved JWT algorithm is required")
        self.issuer = issuer
        self.audience = audience
        self.jwks_uri = jwks_uri
        self.provider_code = provider_code
        self.algorithms = tuple(algorithms)
        self.clock_skew_seconds = clock_skew_seconds
        self.cache_seconds = cache_seconds
        self._jwks_loader = jwks_loader
        self._keys: dict[str, Any] = {}
        self._loaded_at = 0.0
        self._lock = asyncio.Lock()

    @classmethod
    def from_settings(cls) -> OIDCIdentityProvider | None:
        """Return no provider when deployment has not selected a concrete IdP."""
        if not all((settings.OIDC_ISSUER, settings.OIDC_AUDIENCE, settings.OIDC_JWKS_URI)):
            return None
        algorithms = settings.OIDC_ALLOWED_ALGORITHMS
        if isinstance(algorithms, str):
            algorithms = [algorithms]
        return cls(
            issuer=settings.OIDC_ISSUER or "",
            audience=settings.OIDC_AUDIENCE or "",
            jwks_uri=settings.OIDC_JWKS_URI or "",
            provider_code=settings.OIDC_PROVIDER_CODE,
            algorithms=algorithms,
            clock_skew_seconds=settings.OIDC_CLOCK_SKEW_SECONDS,
            cache_seconds=settings.OIDC_JWKS_CACHE_SECONDS,
        )

    async def _fetch_jwks(self) -> dict[str, Any]:
        if self._jwks_loader is not None:
            return await self._jwks_loader()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(self.jwks_uri)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list):
            raise TokenValidationError("invalid JWKS response")
        return payload

    async def _key_for(self, token: str) -> Any:
        try:
            header = jwt.get_unverified_header(token)
        except jwt.exceptions.PyJWTError as exc:
            raise TokenValidationError("malformed token") from exc
        algorithm = header.get("alg")
        key_id = header.get("kid")
        if not isinstance(algorithm, str) or algorithm not in self.algorithms:
            raise TokenValidationError("disallowed token algorithm")
        if not isinstance(key_id, str) or not key_id:
            raise TokenValidationError("token key identity is required")

        now = time.monotonic()
        if key_id in self._keys and now - self._loaded_at <= self.cache_seconds:
            return self._keys[key_id]

        async with self._lock:
            now = time.monotonic()
            if key_id in self._keys and now - self._loaded_at <= self.cache_seconds:
                return self._keys[key_id]
            try:
                payload = await self._fetch_jwks()
                new_keys: dict[str, Any] = {}
                for jwk in payload["keys"]:
                    if not isinstance(jwk, dict) or not isinstance(jwk.get("kid"), str):
                        continue
                    if jwk.get("alg") and jwk["alg"] not in self.algorithms:
                        continue
                    new_keys[jwk["kid"]] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
            except Exception as exc:
                raise TokenValidationError("identity provider key retrieval failed") from exc
            self._keys = new_keys
            self._loaded_at = time.monotonic()
            if key_id not in self._keys:
                raise TokenValidationError("unknown token key identity")
            return self._keys[key_id]

    async def validate_token(self, token: str) -> ValidatedToken:
        """Validate signature and all issuer/audience/time boundaries fail-closed."""
        key = await self._key_for(token)
        try:
            claims = jwt.decode(
                token,
                key=key,
                algorithms=list(self.algorithms),
                audience=self.audience,
                issuer=self.issuer,
                leeway=self.clock_skew_seconds,
                options={"require": ["exp", "sub", "iss", "aud"]},
            )
        except jwt.exceptions.PyJWTError as exc:
            raise TokenValidationError("token verification failed") from exc
        if not isinstance(claims, dict) or not isinstance(claims.get("sub"), str):
            raise TokenValidationError("token subject is required")
        return ValidatedToken(
            issuer=self.issuer,
            subject=claims["sub"],
            claims=dict(claims),
            provider_code=self.provider_code,
        )

    async def resolve_identity(
        self, token: ValidatedToken, session: AsyncSession
    ) -> ResolvedIdentity | None:
        """Map issuer+subject to active local state; token roles are ignored."""
        result = await session.execute(
            select(Actor, ActorIdentity)
            .join(ActorIdentity, ActorIdentity.actor_id == Actor.id)
            .where(
                ActorIdentity.issuer == token.issuer,
                ActorIdentity.subject == token.subject,
                ActorIdentity.provider_code == token.provider_code,
                ActorIdentity.status == "ACTIVE",
                Actor.status == "ACTIVE",
            )
        )
        row = result.first()
        if row is None:
            return None
        actor, identity = row
        await session.execute(
            update(ActorIdentity)
            .where(ActorIdentity.id == identity.id)
            .values(last_seen_at=sa_func_now())
        )
        return ResolvedIdentity(actor=actor, identity=identity)

    def provider_metadata(self) -> dict[str, str | bool]:
        return {
            "protocol": "OIDC/OAuth-compatible JWT",
            "provider_code": self.provider_code,
            "issuer_configured": True,
            "jwks_rotation": True,
            "fail_closed": True,
        }


def sa_func_now() -> Any:
    """Keep the identity module's update expression independent of model metadata."""
    from sqlalchemy import func

    return func.now()


def provider_from_settings() -> IdentityProvider | None:
    """Application factory used by the single FastAPI principal dependency."""
    return OIDCIdentityProvider.from_settings()


def actor_uuid(value: Any) -> uuid.UUID:
    """Narrow helper for typed principal construction."""
    if not isinstance(value, uuid.UUID):
        raise TypeError("actor id is not a UUID")
    return value
