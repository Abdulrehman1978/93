"""Policy-enforced read boundary for encrypted highly sensitive fields."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.db.models import SubjectContact, TranscriptSegment, Translation
from app.errors import AppException
from app.security.authorization import AuthorizationService
from app.security.context import AuthorizationContext
from app.security.encryption import authorized_field_decryption
from app.security.principal import SecurityPrincipal


class SensitiveFieldAccessService:
    """Authorize, decrypt one explicit field, and record the completed read."""

    def __init__(self, authorization: AuthorizationService | None = None) -> None:
        self.authorization = authorization or AuthorizationService()

    async def read_contact_value(
        self,
        principal: SecurityPrincipal,
        contact_id: uuid.UUID,
        context: AuthorizationContext,
        session: AsyncSession,
    ) -> str:
        self._require_exact_reference(context, "contact", contact_id)
        return await self._read(
            principal,
            "contact.read",
            context,
            "subject_contacts.contact_value",
            select(SubjectContact.contact_value).where(SubjectContact.id == contact_id),
            session,
        )

    async def read_transcript_content(
        self,
        principal: SecurityPrincipal,
        transcript_id: uuid.UUID,
        context: AuthorizationContext,
        session: AsyncSession,
    ) -> str:
        self._require_exact_reference(context, "transcript", transcript_id)
        return await self._read(
            principal,
            "transcript.read",
            context,
            "transcript_segments.content",
            select(TranscriptSegment.content).where(TranscriptSegment.id == transcript_id),
            session,
        )

    async def read_translation_content(
        self,
        principal: SecurityPrincipal,
        translation_id: uuid.UUID,
        context: AuthorizationContext,
        session: AsyncSession,
    ) -> str:
        self._require_exact_reference(context, "translation", translation_id)
        return await self._read(
            principal,
            "translation.read",
            context,
            "translations.translated_content",
            select(Translation.translated_content).where(Translation.id == translation_id),
            session,
        )

    async def _read(
        self,
        principal: SecurityPrincipal,
        action: str,
        context: AuthorizationContext,
        field_name: str,
        statement: Select[str],
        session: AsyncSession,
    ) -> str:
        await self.authorization.authorize_or_raise(principal, action, context, session)
        with authorized_field_decryption(field_name):
            value = await session.scalar(statement)
        if not isinstance(value, str):
            raise AppException(
                status_code=404,
                title="Not Found",
                detail="The requested resource is unavailable.",
            )
        await self.authorization.record_resource_read(principal, action, context, session)
        return value

    @staticmethod
    def _require_exact_reference(
        context: AuthorizationContext, resource_type: str, resource_id: uuid.UUID
    ) -> None:
        reference = context.resource
        if (
            reference is None
            or reference.resource_type != resource_type
            or reference.resource_id != str(resource_id)
        ):
            raise AppException(
                status_code=403,
                title="Forbidden",
                detail="The authenticated principal is not authorized for this operation.",
                type_uri="https://api.sambal.gov.in/errors/authorization-denied",
            )
