"""Authenticated application principal, deliberately separate from authorization."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SecurityPrincipal:
    """The locally mapped identity used by every policy decision."""

    actor_id: uuid.UUID
    identity_provider: str
    issuer: str
    external_subject: str
    actor_type: str
    organization_id: uuid.UUID | None = None
    jurisdiction_id: uuid.UUID | None = None
    roles: tuple[str, ...] = ()
    authentication_context: dict[str, Any] = field(default_factory=dict)

    @property
    def is_active_identity(self) -> bool:
        """The principal object can only be built after active-state checks."""
        return True
