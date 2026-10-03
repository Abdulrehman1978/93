"""Authorization request context and safe decision result."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    """The non-secret policy inputs for one protected operation."""

    resource_type: str
    resource_id: str | None = None
    case_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    jurisdiction_id: uuid.UUID | None = None
    purpose: str | None = None
    policy_version_id: uuid.UUID | None = None
    correlation_id: str = "system"
    recipient: str | None = None
    requested_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """Internal decision with reason code; external APIs expose only safe detail."""

    allowed: bool
    reason_code: str
    policy_version: str

    def as_public_dict(self) -> dict[str, bool]:
        """Avoid exposing policy topology to callers."""
        return {"allowed": self.allowed}
