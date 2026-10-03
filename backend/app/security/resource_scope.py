"""Database-authoritative resource-scope resolution for authorization decisions."""

from __future__ import annotations

import uuid
from collections.abc import Awaitable, Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Assessment,
    Case,
    ConsentEvent,
    Interaction,
    ProcessingAuthorization,
    Referral,
    SubjectContact,
    SupportOutcome,
    TranscriptSegment,
    Translation,
)
from app.security.context import ResolvedResourceScope, ResourceReference

SUPPORTED_RESOURCE_TYPES = frozenset(
    {
        "case",
        "referral",
        "assessment",
        "transcript",
        "translation",
        "contact",
        "consent",
        "processing_authorization",
        "support_outcome",
    }
)


class ResourceScopeError(Exception):
    """Safe internal resolver failure with a policy reason code."""

    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


class ResourceScopeResolver:
    """Resolve only trusted scope metadata; never select encrypted payload columns."""

    async def resolve(
        self, reference: ResourceReference, session: AsyncSession
    ) -> ResolvedResourceScope:
        if reference.resource_type not in SUPPORTED_RESOURCE_TYPES:
            raise ResourceScopeError("UNSUPPORTED_RESOURCE_TYPE")
        try:
            resource_id = uuid.UUID(reference.resource_id)
        except ValueError as exc:
            raise ResourceScopeError("INVALID_RESOURCE") from exc

        resolver: Callable[[uuid.UUID, AsyncSession], Awaitable[ResolvedResourceScope | None]] = (
            getattr(self, f"_resolve_{reference.resource_type}")
        )
        scope = await resolver(resource_id, session)
        if scope is None:
            raise ResourceScopeError("RESOURCE_NOT_FOUND")
        return scope

    async def _case_scope(
        self, case_id: uuid.UUID, session: AsyncSession
    ) -> tuple[uuid.UUID | None, uuid.UUID | None, uuid.UUID] | None:
        return (
            await session.execute(
                select(Case.organization_id, Case.jurisdiction_id, Case.subject_id).where(
                    Case.id == case_id
                )
            )
        ).one_or_none()

    async def _resolve_case(
        self, resource_id: uuid.UUID, session: AsyncSession
    ) -> ResolvedResourceScope | None:
        row = await self._case_scope(resource_id, session)
        if row is None:
            return None
        return ResolvedResourceScope(
            "case", resource_id, resource_id, row[0], row[1], subject_id=row[2]
        )

    async def _resolve_referral(
        self, resource_id: uuid.UUID, session: AsyncSession
    ) -> ResolvedResourceScope | None:
        row = (
            await session.execute(
                select(
                    Referral.case_id,
                    Referral.assigned_provider_actor_id,
                    Case.organization_id,
                    Case.jurisdiction_id,
                    Case.subject_id,
                )
                .join(Case, Case.id == Referral.case_id)
                .where(Referral.id == resource_id)
            )
        ).one_or_none()
        if row is None:
            return None
        return ResolvedResourceScope(
            "referral", resource_id, row[0], row[2], row[3], row[1], row[4]
        )

    async def _resolve_assessment(
        self, resource_id: uuid.UUID, session: AsyncSession
    ) -> ResolvedResourceScope | None:
        row = (
            await session.execute(
                select(
                    Assessment.case_id,
                    Case.organization_id,
                    Case.jurisdiction_id,
                    Case.subject_id,
                )
                .join(Case, Case.id == Assessment.case_id)
                .where(Assessment.id == resource_id)
            )
        ).one_or_none()
        if row is None:
            return None
        return ResolvedResourceScope(
            "assessment", resource_id, row[0], row[1], row[2], None, row[3]
        )

    async def _resolve_transcript(
        self, resource_id: uuid.UUID, session: AsyncSession
    ) -> ResolvedResourceScope | None:
        row = (
            await session.execute(
                select(
                    Interaction.case_id,
                    Case.organization_id,
                    Case.jurisdiction_id,
                    Case.subject_id,
                )
                .join(TranscriptSegment, TranscriptSegment.interaction_id == Interaction.id)
                .join(Case, Case.id == Interaction.case_id)
                .where(TranscriptSegment.id == resource_id)
            )
        ).one_or_none()
        if row is None:
            return None
        return ResolvedResourceScope(
            "transcript", resource_id, row[0], row[1], row[2], None, row[3]
        )

    async def _resolve_translation(
        self, resource_id: uuid.UUID, session: AsyncSession
    ) -> ResolvedResourceScope | None:
        row = (
            await session.execute(
                select(
                    Interaction.case_id,
                    Case.organization_id,
                    Case.jurisdiction_id,
                    Case.subject_id,
                )
                .join(TranscriptSegment, TranscriptSegment.interaction_id == Interaction.id)
                .join(Translation, Translation.transcript_segment_id == TranscriptSegment.id)
                .join(Case, Case.id == Interaction.case_id)
                .where(Translation.id == resource_id)
            )
        ).one_or_none()
        if row is None:
            return None
        return ResolvedResourceScope(
            "translation", resource_id, row[0], row[1], row[2], None, row[3]
        )

    async def _resolve_contact(
        self, resource_id: uuid.UUID, session: AsyncSession
    ) -> ResolvedResourceScope | None:
        subject_id = await session.scalar(
            select(SubjectContact.subject_id).where(SubjectContact.id == resource_id)
        )
        if subject_id is None:
            return None
        cases = (
            await session.execute(
                select(Case.id, Case.organization_id, Case.jurisdiction_id).where(
                    Case.subject_id == subject_id
                )
            )
        ).all()
        if len(cases) > 1:
            raise ResourceScopeError("AMBIGUOUS_RESOURCE_SCOPE")
        if not cases:
            return ResolvedResourceScope("contact", resource_id, subject_id=subject_id)
        row = cases[0]
        return ResolvedResourceScope(
            "contact", resource_id, row[0], row[1], row[2], None, subject_id
        )

    async def _resolve_consent(
        self, resource_id: uuid.UUID, session: AsyncSession
    ) -> ResolvedResourceScope | None:
        row = (
            await session.execute(
                select(ConsentEvent.case_id, ConsentEvent.subject_id).where(
                    ConsentEvent.id == resource_id
                )
            )
        ).one_or_none()
        if row is None:
            return None
        if row[0] is None:
            return ResolvedResourceScope("consent", resource_id, subject_id=row[1])
        case_scope = await self._case_scope(row[0], session)
        if case_scope is None:
            return None
        return ResolvedResourceScope(
            "consent", resource_id, row[0], case_scope[0], case_scope[1], None, row[1]
        )

    async def _resolve_processing_authorization(
        self, resource_id: uuid.UUID, session: AsyncSession
    ) -> ResolvedResourceScope | None:
        row = (
            await session.execute(
                select(
                    ProcessingAuthorization.case_id,
                    ProcessingAuthorization.interaction_id,
                ).where(ProcessingAuthorization.id == resource_id)
            )
        ).one_or_none()
        if row is None:
            return None
        case_id = row[0]
        if case_id is None and row[1] is not None:
            case_id = await session.scalar(
                select(Interaction.case_id).where(Interaction.id == row[1])
            )
        if case_id is None:
            return ResolvedResourceScope("processing_authorization", resource_id)
        case_scope = await self._case_scope(case_id, session)
        if case_scope is None:
            return None
        return ResolvedResourceScope(
            "processing_authorization",
            resource_id,
            case_id,
            case_scope[0],
            case_scope[1],
            subject_id=case_scope[2],
        )

    async def _resolve_support_outcome(
        self, resource_id: uuid.UUID, session: AsyncSession
    ) -> ResolvedResourceScope | None:
        row = (
            await session.execute(
                select(
                    Referral.case_id,
                    Referral.assigned_provider_actor_id,
                    Case.organization_id,
                    Case.jurisdiction_id,
                    Case.subject_id,
                )
                .join(SupportOutcome, SupportOutcome.referral_id == Referral.id)
                .join(Case, Case.id == Referral.case_id)
                .where(SupportOutcome.id == resource_id)
            )
        ).one_or_none()
        if row is None:
            return None
        return ResolvedResourceScope(
            "support_outcome", resource_id, row[0], row[2], row[3], row[1], row[4]
        )
