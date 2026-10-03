"""Server-derived lawful processing authorization service."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel.schemas import ConsentMode
from app.db.models.casework import Interaction
from app.db.models.governance import (
    PolicyVersion,
    ProcessingAuthorityType,
    ProcessingAuthorization,
    ProcessingPurpose,
)
from app.db.models.platform import AuditEvent
from app.errors import AppException
from app.privacy.policies import ensure_packet06_catalog, resolve_purpose
from app.security.authorization import AuthorizationService
from app.security.context import AuthorizationContext
from app.security.principal import SecurityPrincipal


async def _purpose_rows(
    session: AsyncSession, purpose_code: str
) -> tuple[ProcessingPurpose, ProcessingAuthorityType, PolicyVersion]:
    policy = await ensure_packet06_catalog(session)
    policy_row = await session.scalar(select(PolicyVersion).where(PolicyVersion.id == policy.id))
    purpose = await session.scalar(
        select(ProcessingPurpose).where(ProcessingPurpose.purpose_code == purpose_code)
    )
    if purpose is None or not purpose.is_active or policy_row is None:
        raise AppException(
            404,
            "Purpose unavailable",
            "The requested processing purpose is unavailable.",
            "https://api.sambal.gov.in/errors/purpose-unavailable",
        )
    authority = await session.scalar(
        select(ProcessingAuthorityType).where(
            ProcessingAuthorityType.authority_code == purpose.default_authority_code
        )
    )
    if authority is None:
        raise AppException(
            503,
            "Policy unavailable",
            "The processing policy is not configured.",
            "https://api.sambal.gov.in/errors/policy-unavailable",
        )
    return purpose, authority, policy_row


async def create_interaction_authorization(
    session: AsyncSession,
    interaction: Interaction,
    purpose_code: str,
    *,
    actor: SecurityPrincipal | None = None,
    emergency_authority: str | None = None,
) -> ProcessingAuthorization:
    policy = resolve_purpose(purpose_code)
    if emergency_authority is None and policy.consent_mode in {
        ConsentMode.REQUIRED,
        ConsentMode.OPTIONAL,
    }:
        raise AppException(
            409,
            "Consent required",
            "This purpose must be authorized through the consent ledger.",
            "https://api.sambal.gov.in/errors/consent-required",
        )
    if emergency_authority is not None or policy.human_approval_required:
        if actor is None or actor.actor_type != "STAFF" or interaction.case_id is None:
            raise AppException(
                403,
                "Human authorization required",
                "This purpose requires an active human supervisor.",
                "https://api.sambal.gov.in/errors/human-authorization-required",
            )
        if emergency_authority not in policy.allowed_lawful_authorities:
            raise AppException(
                400,
                "Invalid emergency authority",
                "The emergency authority is not permitted.",
                "https://api.sambal.gov.in/errors/invalid-authority",
            )
    purpose_row, authority_row, policy_row = await _purpose_rows(session, purpose_code)
    if emergency_authority is not None:
        emergency_authority_row = await session.scalar(
            select(ProcessingAuthorityType).where(
                ProcessingAuthorityType.authority_code == emergency_authority
            )
        )
        if emergency_authority_row is None:
            raise AppException(
                503,
                "Policy unavailable",
                "The emergency authority is not configured.",
                "https://api.sambal.gov.in/errors/policy-unavailable",
            )
        authority_row = emergency_authority_row
    if authority_row.authority_code not in policy.allowed_lawful_authorities:
        raise AppException(
            400,
            "Invalid authority",
            "The authority is not permitted for this purpose.",
            "https://api.sambal.gov.in/errors/invalid-authority",
        )
    if actor is not None:
        if interaction.case_id is None or actor.actor_type != "STAFF":
            raise AppException(
                403,
                "Human authorization required",
                "Only an active staff principal may authorize this purpose.",
                "https://api.sambal.gov.in/errors/human-authorization-required",
            )
        await AuthorizationService().authorize_or_raise(
            actor,
            "processing_authorization.manage",
            AuthorizationContext.for_resource(
                "case",
                interaction.case_id,
                purpose=purpose_code,
                correlation_id=f"processing-authorization:{interaction.id}",
            ),
            session,
        )
    authorization = ProcessingAuthorization(
        case_id=interaction.case_id if actor is not None else None,
        interaction_id=interaction.id,
        processing_purpose_id=purpose_row.id,
        authority_type_id=authority_row.id,
        actor_id=actor.actor_id if actor else None,
        authorization_reason=(
            "Human staff principal authorized a documented lawful processing authority."
            if actor
            else "Information was voluntarily provided for the specified intake purpose."
        ),
        policy_version_id=policy_row.id,
    )
    session.add(authorization)
    await session.flush()
    session.add(
        AuditEvent(
            actor_id=actor.actor_id if actor else None,
            action="PROCESSING_AUTHORIZATION_CREATED",
            entity_type="processing_authorization",
            entity_id=str(authorization.id),
            purpose=purpose_code,
            policy_version_id=policy_row.id,
            safe_metadata={"scope": "interaction", "authority": authority_row.authority_code},
        )
    )
    await session.flush()
    return authorization


async def promote_interaction_authorizations_to_case(
    session: AsyncSession, interaction: Interaction, case_id: uuid.UUID
) -> None:
    authorizations = (
        await session.scalars(
            select(ProcessingAuthorization)
            .where(
                ProcessingAuthorization.interaction_id == interaction.id,
                ProcessingAuthorization.status == "ACTIVE",
            )
            .with_for_update()
        )
    ).all()
    for authorization in authorizations:
        existing = await session.scalar(
            select(ProcessingAuthorization).where(
                ProcessingAuthorization.case_id == case_id,
                ProcessingAuthorization.processing_purpose_id
                == authorization.processing_purpose_id,
                ProcessingAuthorization.authority_type_id == authorization.authority_type_id,
                ProcessingAuthorization.status == "ACTIVE",
            )
        )
        if existing is None:
            session.add(
                ProcessingAuthorization(
                    case_id=case_id,
                    interaction_id=interaction.id,
                    processing_purpose_id=authorization.processing_purpose_id,
                    authority_type_id=authorization.authority_type_id,
                    consent_event_id=authorization.consent_event_id,
                    actor_id=authorization.actor_id,
                    authorization_reason="Promoted from interaction scope at case binding.",
                    policy_version_id=authorization.policy_version_id,
                    expires_at=authorization.expires_at,
                )
            )
    await session.flush()
