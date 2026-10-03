"""Deny-by-default hybrid RBAC/ABAC policy decision and enforcement point."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import exists, false, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db.models import (
    AccessElevation,
    Actor,
    ActorRoleBinding,
    AuditEvent,
    CaseParticipant,
    ProcessingAuthorization,
    ProcessingPurpose,
    Role,
)
from app.errors import AppException
from app.security.context import (
    AuthorizationContext,
    AuthorizationDecision,
    ResolvedResourceScope,
)
from app.security.permissions import (
    ACTION_RESOURCE_TYPES,
    ASSIGNMENT_REQUIRED_ROLES,
    CASE_SCOPED_ACTIONS,
    CREATION_ACTIONS,
    GLOBAL_ACTIONS,
    KNOWN_ACTIONS,
    PERMISSION_REGISTRY_VERSION,
    PROVIDER_ROLES,
    ROLE_PERMISSIONS,
    SENSITIVE_ACTIONS,
)
from app.security.principal import SecurityPrincipal
from app.security.resource_scope import ResourceScopeError, ResourceScopeResolver


class AuthorizationService:
    """One policy decision point used by protected routes and domain services."""

    def __init__(self, resolver: ResourceScopeResolver | None = None) -> None:
        self.resolver = resolver or ResourceScopeResolver()

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
        """Resolve persistent scope internally, decide, and append a safe audit row."""
        if action not in KNOWN_ACTIONS:
            return await self._decision(
                principal, action, context, session, False, "UNKNOWN_ACTION"
            )

        actor = await session.scalar(
            select(Actor).where(Actor.id == principal.actor_id, Actor.status == "ACTIVE")
        )
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

        scope: ResolvedResourceScope | None = None
        if action in GLOBAL_ACTIONS:
            if context.resource is not None or context.intended_creation_scope is not None:
                return await self._decision(
                    principal, action, context, session, False, "GLOBAL_SCOPE_REQUIRED"
                )
        else:
            if context.resource is None:
                return await self._decision(
                    principal, action, context, session, False, "RESOURCE_REQUIRED"
                )
            try:
                scope = await self.resolver.resolve(context.resource, session)
            except ResourceScopeError as exc:
                return await self._decision(
                    principal, action, context, session, False, exc.reason_code
                )
            expected_types = ACTION_RESOURCE_TYPES.get(action)
            if expected_types is None or scope.resource_type not in expected_types:
                return await self._decision(
                    principal, action, context, session, False, "RESOURCE_TYPE_MISMATCH"
                )
            if context.intended_creation_scope is not None and (
                action not in CREATION_ACTIONS or not self._creation_scope_matches(context, scope)
            ):
                return await self._decision(
                    principal, action, context, session, False, "UNTRUSTED_SCOPE_OVERRIDE"
                )

        matching_roles: list[str] = []
        for binding, role_code in binding_rows:
            if action not in ROLE_PERMISSIONS.get(role_code, frozenset()):
                continue
            if scope is not None and not await self._scope_matches(
                binding.organization_id,
                binding.jurisdiction_id,
                scope.organization_id,
                scope.jurisdiction_id,
                session,
            ):
                continue
            if scope is None and (
                binding.organization_id is not None or binding.jurisdiction_id is not None
            ):
                continue
            matching_roles.append(role_code)

        has_permission = bool(matching_roles)
        if not has_permission and scope is not None:
            can_break_glass = any(
                "access.break_glass" in ROLE_PERMISSIONS.get(role_code, frozenset())
                for _, role_code in binding_rows
            )
            has_permission = can_break_glass and await self._active_elevation_matches(
                principal.actor_id, action, scope, session
            )
        if not has_permission:
            return await self._decision(
                principal, action, context, session, False, "PERMISSION_DENIED"
            )

        if scope is not None and action in CASE_SCOPED_ACTIONS:
            if scope.case_id is None:
                return await self._decision(
                    principal, action, context, session, False, "RESOURCE_CASE_REQUIRED"
                )
            if any(role in ASSIGNMENT_REQUIRED_ROLES for role in matching_roles):
                assigned = await session.scalar(
                    select(
                        exists().where(
                            CaseParticipant.case_id == scope.case_id,
                            CaseParticipant.actor_id == principal.actor_id,
                        )
                    )
                )
                if not assigned:
                    return await self._decision(
                        principal, action, context, session, False, "CASE_NOT_ASSIGNED"
                    )

        if any(role in PROVIDER_ROLES for role in matching_roles):
            if scope is None or scope.resource_type not in {"referral", "support_outcome"}:
                return await self._decision(
                    principal, action, context, session, False, "PROVIDER_SCOPE_REQUIRED"
                )
            if scope.assigned_provider_actor_id != principal.actor_id:
                return await self._decision(
                    principal, action, context, session, False, "PROVIDER_NOT_ASSIGNED"
                )

        if action in SENSITIVE_ACTIONS:
            if not context.request.purpose:
                return await self._decision(
                    principal, action, context, session, False, "PURPOSE_REQUIRED"
                )
            if scope is None or scope.case_id is None:
                return await self._decision(
                    principal, action, context, session, False, "RESOURCE_CASE_REQUIRED"
                )
            if not await self._purpose_authorized(scope.case_id, context, session):
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

    async def record_resource_read(
        self,
        principal: SecurityPrincipal,
        action: str,
        context: AuthorizationContext,
        session: AsyncSession,
    ) -> None:
        """Distinguish an actual sensitive read from the preceding policy decision."""
        reference = context.resource
        if reference is None:
            raise ValueError("resource read audit requires a resource reference")
        session.add(
            AuditEvent(
                actor_id=principal.actor_id,
                action=action,
                entity_type=reference.resource_type,
                entity_id=reference.resource_id,
                reason="resource read",
                correlation_id=context.request.correlation_id,
                safe_metadata={
                    "event_type": "RESOURCE_READ",
                    "registry_version": PERMISSION_REGISTRY_VERSION,
                },
                decision="ALLOW",
                reason_code="RESOURCE_READ",
                purpose=context.request.purpose,
                policy_version_id=context.request.policy_version_id,
            )
        )
        await session.flush()

    def _creation_scope_matches(
        self, context: AuthorizationContext, scope: ResolvedResourceScope
    ) -> bool:
        intended = context.intended_creation_scope
        if intended is None:
            return True
        return all(
            (
                intended.case_id is None or intended.case_id == scope.case_id,
                intended.organization_id is None
                or intended.organization_id == scope.organization_id,
                intended.jurisdiction_id is None
                or intended.jurisdiction_id == scope.jurisdiction_id,
            )
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
        scope: ResolvedResourceScope,
        session: AsyncSession,
    ) -> bool:
        approver = aliased(Actor)
        exact_resource = (AccessElevation.resource_type == scope.resource_type) & (
            AccessElevation.resource_id == str(scope.resource_id)
        )
        case_resource = (
            (AccessElevation.case_id == scope.case_id) if scope.case_id is not None else false()
        )
        result = await session.execute(
            select(AccessElevation.id)
            .join(approver, approver.id == AccessElevation.approved_by_actor_id)
            .where(
                AccessElevation.actor_id == actor_id,
                AccessElevation.requested_permission == action,
                AccessElevation.status == "ACTIVE",
                AccessElevation.effective_from <= datetime.now(UTC),
                AccessElevation.expires_at > datetime.now(UTC),
                AccessElevation.approved_by_actor_id.is_not(None),
                AccessElevation.approved_by_actor_id != actor_id,
                approver.actor_type.in_(("STAFF", "AUDITOR")),
                approver.status == "ACTIVE",
                or_(exact_resource, case_resource),
            )
        )
        return result.scalar_one_or_none() is not None

    async def _purpose_authorized(
        self,
        case_id: uuid.UUID,
        context: AuthorizationContext,
        session: AsyncSession,
    ) -> bool:
        query = select(
            exists().where(
                ProcessingAuthorization.case_id == case_id,
                ProcessingAuthorization.processing_purpose_id == ProcessingPurpose.id,
                ProcessingPurpose.purpose_code == context.request.purpose,
                ProcessingPurpose.is_active.is_(True),
                ProcessingAuthorization.created_at <= datetime.now(UTC),
                or_(
                    ProcessingAuthorization.expires_at.is_(None),
                    ProcessingAuthorization.expires_at > datetime.now(UTC),
                ),
            )
        )
        if context.request.policy_version_id is not None:
            query = query.where(
                ProcessingAuthorization.policy_version_id == context.request.policy_version_id
            )
        return bool(await session.scalar(query))

    async def _decision(
        self,
        principal: SecurityPrincipal,
        action: str,
        context: AuthorizationContext,
        session: AsyncSession,
        allowed: bool,
        reason_code: str,
    ) -> AuthorizationDecision:
        reference = context.resource
        session.add(
            AuditEvent(
                actor_id=principal.actor_id,
                action=action,
                entity_type=reference.resource_type if reference else "global",
                entity_id=reference.resource_id if reference else "global",
                reason="authorization decision",
                correlation_id=context.request.correlation_id,
                safe_metadata={
                    "event_type": "AUTHORIZATION_DECISION",
                    "registry_version": PERMISSION_REGISTRY_VERSION,
                },
                decision="ALLOW" if allowed else "DENY",
                reason_code=reason_code,
                purpose=context.request.purpose,
                policy_version_id=context.request.policy_version_id,
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
