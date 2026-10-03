"""Separated request inputs and trusted resource authorization metadata."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ResourceReference:
    """Opaque reference to an existing persistent object."""

    resource_type: str
    resource_id: str


@dataclass(frozen=True, slots=True)
class AuthorizationRequestContext:
    """Caller-supplied request facts that cannot redefine persistent scope."""

    purpose: str | None = None
    policy_version_id: uuid.UUID | None = None
    correlation_id: str = "system"
    recipient: str | None = None
    requested_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class IntendedCreationScope:
    """Explicit intended scope used only for creation under an existing parent."""

    case_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    jurisdiction_id: uuid.UUID | None = None
    assigned_provider_actor_id: uuid.UUID | None = None


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    """Policy input with request facts separated from database-resolved scope."""

    resource: ResourceReference | None = None
    request: AuthorizationRequestContext = field(default_factory=AuthorizationRequestContext)
    intended_creation_scope: IntendedCreationScope | None = None

    @classmethod
    def for_resource(
        cls,
        resource_type: str,
        resource_id: str | uuid.UUID,
        *,
        purpose: str | None = None,
        policy_version_id: uuid.UUID | None = None,
        correlation_id: str = "system",
        recipient: str | None = None,
        intended_creation_scope: IntendedCreationScope | None = None,
    ) -> AuthorizationContext:
        return cls(
            resource=ResourceReference(resource_type, str(resource_id)),
            request=AuthorizationRequestContext(
                purpose=purpose,
                policy_version_id=policy_version_id,
                correlation_id=correlation_id,
                recipient=recipient,
            ),
            intended_creation_scope=intended_creation_scope,
        )


@dataclass(frozen=True, slots=True)
class ResolvedResourceScope:
    """Trusted authorization metadata read from PostgreSQL without sensitive payloads."""

    resource_type: str
    resource_id: uuid.UUID
    case_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    jurisdiction_id: uuid.UUID | None = None
    assigned_provider_actor_id: uuid.UUID | None = None
    subject_id: uuid.UUID | None = None


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """Internal decision with reason code; external APIs expose only safe detail."""

    allowed: bool
    reason_code: str
    policy_version: str

    def as_public_dict(self) -> dict[str, bool]:
        """Avoid exposing policy topology to callers."""
        return {"allowed": self.allowed}
