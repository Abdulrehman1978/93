"""Deny-by-default hybrid RBAC/ABAC policy decision and enforcement point."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AccessElevation,
    Actor,
    ActorRoleBinding,
    AuditEvent,
    Case,
    CaseParticipant,
    ProcessingAuthorization,
    ProcessingPurpose,
    Referral,
    Role,
)
from app.errors import AppException
from app.security.context import AuthorizationContext, AuthorizationDecision
from app.security.permissions import (
    ASSIGNMENT_REQUIRED_ROLES,
    CASE_SCOPED_ACTIONS,
    KNOWN_ACTIONS,
    PERMISSION_REGISTRY_VERSION,
    PROVIDER_ROLES,
    ROLE_PERMISSIONS,
    SENSITIVE_ACTIONS,
)
from app.security.principal import SecurityPrincipal


class AuthorizationService:
    """One policy decision point used by protected routes and domain services."""

    async def load_principal(
        self,
        actor: Actor,
        *,
        provider_code: str,
        issuer: str,
        external_subject: str,
        authentication_context: dict[str, Any],
        session: AsyncSession,
    ) -> SecurityPrincipal:
        rows = (
            await session.execute(
                select(Role.code)
                .join(ActorRoleBinding, ActorRoleBinding.role_id == Role.id)
                .where(
                    ActorRoleBinding.actor_id == actor.id,
                    Role.status == "ACTIVE",
                    ActorRoleBinding.effective_from <= datetime.now(UTC),
                    or_(
                        ActorRoleBinding.effective_to.is_(None),
                        ActorRoleBinding.effective_to > datetime.now(UTC),
                    ),
                )
            )
        ).scalars()
        return SecurityPrincipal(
            actor_id=actor.id,
            identity_provider=provider_code,
            issuer=issuer,
            external_subject=external_subject,
            actor_type=actor.actor_type,
            organization_id=actor.organization_id,
            jurisdiction_id=actor.jurisdiction_id,
            roles=tuple(rows),
            authentication_context=authentication_context,
        )

    async def authorize(
        self,
        principal: SecurityPrincipal,
        action: str,
        context: AuthorizationContext,
        session: AsyncSession,
    ) -> AuthorizationDecision:
        """Return ALLOW/DENY and record a safe decision audit before any data read."""
        if action not in KNOWN_ACTIONS:
            return await self._decision(
                principal, action, context, session, False, "UNKNOWN_ACTION"
            )

        actor = (
            await session.execute(
                select(Actor).where(Actor.id == principal.actor_id, Actor.status == "ACTIVE")
            )
        ).scalar_one_or_none()
        if actor is None:
            return await self._decision(
                principal, action, context, session, False, "ACTOR_INACTIVE"
            )

        binding_rows = (
            await session.execute(
                select(ActorRoleBinding, Role.code)
                .join(Role, Role.id == ActorRoleBinding.role_id)
                .where(
                    ActorRoleBinding.actor_id == principal.actor_id,
                    Role.status == "ACTIVE",
                    ActorRoleBinding.effective_from <= datetime.now(UTC),
                    or_(
                        ActorRoleBinding.effective_to.is_(None),
                        ActorRoleBinding.effective_to > datetime.now(UTC),
                    ),
                )
            )
        ).all()
        if not binding_rows:
            return await self._decision(
                principal, action, context, session, False, "NO_ACTIVE_ROLE"
            )

        target_case_id = context.case_id
        if target_case_id is None and context.resource_type == "case" and context.resource_id:
            try:
                target_case_id = uuid.UUID(context.resource_id)
            except ValueError:
                return await self._decision(
                    principal, action, context, session, False, "INVALID_RESOURCE"
                )

        case_scope: tuple[uuid.UUID | None, uuid.UUID | None] | None = None
        if target_case_id is not None:
            case_scope = (
                await session.execute(
                    select(Case.organization_id, Case.jurisdiction_id).where(
                        Case.id == target_case_id
                    )
                )
            ).one_or_none()
            if case_scope is None:
                return await self._decision(
                    principal, action, context, session, False, "RESOURCE_NOT_FOUND"
                )

        resource_org = context.organization_id or (case_scope[0] if case_scope else None)
        resource_jurisdiction = context.jurisdiction_id or (case_scope[1] if case_scope else None)

        matching_roles: list[str] = []
        for binding, role_code in binding_rows:
            permissions = ROLE_PERMISSIONS.get(role_code, frozenset())
            if action not in permissions:
                continue
            if not await self._scope_matches(
                binding.organization_id,
                binding.jurisdiction_id,
                resource_org,
                resource_jurisdiction,
                session,
            ):
                continue
            matching_roles.append(role_code)

        has_permission = bool(matching_roles)
        if not has_permission:
            can_break_glass = any(
                "access.break_glass" in ROLE_PERMISSIONS.get(role_code, frozenset())
                for _, role_code in binding_rows
            )
            has_permission = can_break_glass and await self._active_elevation_matches(
                principal.actor_id, action, context, session
            )
        if not has_permission:
            return await self._decision(
                principal, action, context, session, False, "PERMISSION_DENIED"
            )

        if target_case_id is not None and action in CASE_SCOPED_ACTIONS:
            if any(role in ASSIGNMENT_REQUIRED_ROLES for role in matching_roles):
                assigned = await session.scalar(
                    select(
                        exists().where(
                            CaseParticipant.case_id == target_case_id,
                            CaseParticipant.actor_id == principal.actor_id,
                        )
                    )
                )
                if not assigned:
                    return await self._decision(
                        principal, action, context, session, False, "CASE_NOT_ASSIGNED"
                    )

            if any(role in PROVIDER_ROLES for role in matching_roles):
                if context.resource_type != "referral" or context.resource_id is None:
                    return await self._decision(
                        principal, action, context, session, False, "PROVIDER_SCOPE_REQUIRED"
                    )
                try:
                    referral_id = uuid.UUID(context.resource_id)
                except ValueError:
                    return await self._decision(
                        principal, action, context, session, False, "INVALID_RESOURCE"
                    )
                assigned_provider = await session.scalar(
                    select(Referral.assigned_provider_actor_id).where(Referral.id == referral_id)
                )
                if assigned_provider != principal.actor_id:
                    return await self._decision(
                        principal, action, context, session, False, "PROVIDER_NOT_ASSIGNED"
                    )

        if action in SENSITIVE_ACTIONS:
            if not context.purpose:
                return await self._decision(
                    principal, action, context, session, False, "PURPOSE_REQUIRED"
                )
            if target_case_id is not None:
                purpose_query = select(
                    exists().where(
                        ProcessingAuthorization.case_id == target_case_id,
                        ProcessingAuthorization.processing_purpose_id == ProcessingPurpose.id,
                        ProcessingPurpose.purpose_code == context.purpose,
                        ProcessingAuthorization.expires_at.is_(None)
                        | (ProcessingAuthorization.expires_at > datetime.now(UTC)),
                    )
                )
                if context.policy_version_id is not None:
                    purpose_query = purpose_query.where(
                        ProcessingAuthorization.policy_version_id == context.policy_version_id
                    )
                if not await session.scalar(purpose_query):
                    return await self._decision(
                        principal, action, context, session, False, "PURPOSE_NOT_AUTHORIZED"
                    )

        return await self._decision(principal, action, context, session, True, "ALLOW")

    async def authorize_or_raise(
        self,
        principal: SecurityPrincipal,
        action: str,
        context: AuthorizationContext,
        session: AsyncSession,
    ) -> AuthorizationDecision:
        decision = await self.authorize(principal, action, context, session)
        if decision.allowed:
            return decision
        status_code = 404 if decision.reason_code == "RESOURCE_NOT_FOUND" else 403
        raise AppException(
            status_code=status_code,
            title="Not Found" if status_code == 404 else "Forbidden",
            detail=(
                "The requested resource is unavailable."
                if status_code == 404
                else "The authenticated principal is not authorized for this operation."
            ),
            type_uri="https://api.sambal.gov.in/errors/authorization-denied",
        )

    async def _scope_matches(
        self,
        binding_org: uuid.UUID | None,
        binding_jurisdiction: uuid.UUID | None,
        resource_org: uuid.UUID | None,
        resource_jurisdiction: uuid.UUID | None,
        session: AsyncSession,
    ) -> bool:
        if binding_org is not None and binding_org != resource_org:
            return False
        if binding_jurisdiction is None:
            return True
        if resource_jurisdiction is None:
            return False
        hierarchy = sa_text(
            """
            WITH RECURSIVE scope AS (
                SELECT id, parent_id FROM jurisdictions WHERE id = :resource_jurisdiction
                UNION ALL
                SELECT j.id, j.parent_id FROM jurisdictions j JOIN scope s ON j.id = s.parent_id
            )
            SELECT EXISTS(SELECT 1 FROM scope WHERE id = :binding_jurisdiction)
            """
        )
        return bool(
            await session.scalar(
                hierarchy,
                {
                    "resource_jurisdiction": resource_jurisdiction,
                    "binding_jurisdiction": binding_jurisdiction,
                },
            )
        )

    async def _active_elevation_matches(
        self,
        actor_id: uuid.UUID,
        action: str,
        context: AuthorizationContext,
        session: AsyncSession,
    ) -> bool:
        if context.case_id is None and context.resource_id is None:
            return False
        scope_filter = (
            AccessElevation.case_id == context.case_id
            if context.case_id is not None
            else AccessElevation.resource_id == context.resource_id
        )
        return bool(
            await session.scalar(
                select(AccessElevation.id).where(
                    AccessElevation.actor_id == actor_id,
                    AccessElevation.requested_permission == action,
                    AccessElevation.status == "ACTIVE",
                    AccessElevation.effective_from <= datetime.now(UTC),
                    AccessElevation.expires_at > datetime.now(UTC),
                    scope_filter,
                )
            )
        )

    async def _decision(
        self,
        principal: SecurityPrincipal,
        action: str,
        context: AuthorizationContext,
        session: AsyncSession,
        allowed: bool,
        reason_code: str,
    ) -> AuthorizationDecision:
        session.add(
            AuditEvent(
                actor_id=principal.actor_id,
                action=action,
                entity_type=context.resource_type,
                entity_id=context.resource_id or str(context.case_id or "unknown"),
                reason="authorization decision",
                correlation_id=context.correlation_id,
                safe_metadata={"registry_version": PERMISSION_REGISTRY_VERSION},
                decision="ALLOW" if allowed else "DENY",
                reason_code=reason_code,
                purpose=context.purpose,
                policy_version_id=context.policy_version_id,
            )
        )
        await session.flush()
        return AuthorizationDecision(
            allowed=allowed,
            reason_code=reason_code,
            policy_version=PERMISSION_REGISTRY_VERSION,
        )


def sa_text(value: str) -> Any:
    from sqlalchemy import text

    return text(value)
