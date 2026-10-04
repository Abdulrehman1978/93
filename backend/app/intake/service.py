"""Atomic, idempotent citizen intake submission service."""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel.registry import InteractionMode
from app.channel.session import ChannelSessionService
from app.db.models.casework import (
    Case,
    CaseStatusEvent,
    CitizenIntakeEntry,
    Interaction,
    InteractionEvent,
    SubjectContact,
)
from app.db.models.governance import (
    ProcessingAuthorityType,
    ProcessingAuthorization,
    ProcessingPurpose,
)
from app.db.models.platform import AuditEvent
from app.errors import AppException
from app.intake.schemas import IntakeSubmissionResponse, SilentIntakeRequest, WriteIntakeRequest
from app.privacy.processing_authorization import promote_interaction_authorizations_to_case


class CitizenIntakeService:
    """Own the one-transaction Write/Silent submission boundary."""

    def __init__(self, sessions: ChannelSessionService | None = None) -> None:
        self.sessions = sessions or ChannelSessionService()

    async def submit_write(
        self,
        session: AsyncSession,
        session_id: uuid.UUID,
        raw_token: str,
        request: WriteIntakeRequest,
    ) -> IntakeSubmissionResponse:
        entries = [("NARRATIVE", "WRITE_NARRATIVE", request.narrative)]
        optional_entries = (
            ("STRUCTURED_ANSWER", "INCIDENT_WHEN", request.optional_when),
            ("STRUCTURED_ANSWER", "INCIDENT_LOCATION", request.optional_location),
            ("STRUCTURED_ANSWER", "CURRENT_SAFETY", request.optional_current_safety),
            ("STRUCTURED_ANSWER", "CONTACT_PREFERENCE", request.optional_contact_preference),
        )
        entries.extend(
            (entry_type, question_code, value.value if isinstance(value, StrEnum) else value)
            for entry_type, question_code, value in optional_entries
            if value is not None
        )
        return await self._submit(
            session,
            session_id,
            raw_token,
            request.client_submission_id,
            InteractionMode.TEXT,
            entries,
            request.optional_contact_value,
        )

    async def submit_silent(
        self,
        session: AsyncSession,
        session_id: uuid.UUID,
        raw_token: str,
        request: SilentIntakeRequest,
    ) -> IntakeSubmissionResponse:
        entries = [
            ("STRUCTURED_ANSWER", "CURRENT_SAFETY", request.current_safety.value),
            ("STRUCTURED_ANSWER", "URGENT_HELP", request.urgent_help.value),
            ("STRUCTURED_ANSWER", "CONTACT_PREFERENCE", request.contact_preference.value),
        ]
        return await self._submit(
            session,
            session_id,
            raw_token,
            request.client_submission_id,
            InteractionMode.SILENT,
            entries,
            request.optional_contact_value,
        )

    async def _submit(
        self,
        session: AsyncSession,
        session_id: uuid.UUID,
        raw_token: str,
        client_submission_id: str,
        expected_mode: InteractionMode,
        entries: list[tuple[str, str, str]],
        contact_value: str | None,
    ) -> IntakeSubmissionResponse:
        interaction = await self.sessions.authenticate_submission(session, session_id, raw_token)
        if interaction.channel != "WEB":
            raise AppException(
                403,
                "Public intake unavailable",
                "This intake boundary is available only through the public web channel.",
                "https://api.sambal.gov.in/errors/intake-channel-unavailable",
            )
        existing_entry = await session.scalar(
            select(CitizenIntakeEntry.id).where(
                CitizenIntakeEntry.interaction_id == interaction.id,
                CitizenIntakeEntry.client_submission_id == client_submission_id,
            )
        )
        if existing_entry is not None:
            if interaction.status != "COMPLETED":
                raise AppException(
                    409,
                    "Submission in progress",
                    "This submission is already being processed.",
                    "https://api.sambal.gov.in/errors/submission-in-progress",
                )
            return await self._receipt_for_interaction(session, interaction, client_submission_id)
        if interaction.status != "OPEN":
            raise AppException(
                409,
                "Session already submitted",
                "This session has already received an intake.",
                "https://api.sambal.gov.in/errors/session-already-submitted",
            )
        if InteractionMode(interaction.interaction_mode) is not expected_mode:
            raise AppException(
                409,
                "Interaction mode mismatch",
                "Choose the selected intake mode before submitting.",
                "https://api.sambal.gov.in/errors/intake-mode-mismatch",
            )
        await self._require_intake_authorization(session, interaction)
        now = datetime.now(UTC)
        tracking_reference = self._tracking_reference(now.year)
        case = Case(
            id=uuid.uuid4(),
            public_tracking_id=tracking_reference,
            subject_id=interaction.subject_id,
            status="OPEN",
            priority="NORMAL",
        )
        session.add(case)
        await session.flush()
        for sequence, (entry_type, question_code, content) in enumerate(entries, start=1):
            session.add(
                CitizenIntakeEntry(
                    interaction_id=interaction.id,
                    sequence=sequence,
                    entry_type=entry_type,
                    question_code=question_code,
                    content=content,
                    language=interaction.language or "en",
                    client_submission_id=client_submission_id,
                )
            )
        if contact_value is not None:
            session.add(
                SubjectContact(
                    subject_id=interaction.subject_id,
                    channel="PHONE",
                    contact_value=contact_value,
                    is_primary=False,
                    safe_to_use=False,
                )
            )
        interaction.case_id = case.id
        await promote_interaction_authorizations_to_case(session, interaction, case.id)
        session.add(
            CaseStatusEvent(
                case_id=case.id,
                previous_status=None,
                new_status="OPEN",
                reason="Citizen intake received through the public gateway.",
            )
        )
        session.add(
            InteractionEvent(
                interaction_id=interaction.id,
                event_type="CITIZEN_INTAKE_SUBMITTED",
                occurred_at=now,
                source_reference=f"intake-submission:{client_submission_id}",
                event_metadata={
                    "interaction_mode": expected_mode.value,
                    "entry_count": len(entries),
                },
            )
        )
        session.add(
            AuditEvent(
                action="CITIZEN_INTAKE_SUBMITTED",
                entity_type="case",
                entity_id=str(case.id),
                purpose="PURP-01",
                safe_metadata={
                    "interaction_mode": expected_mode.value,
                    "entry_count": len(entries),
                    "tracking_reference": tracking_reference,
                },
            )
        )
        interaction.status = "COMPLETED"
        interaction.ended_at = now
        await session.flush()
        return IntakeSubmissionResponse(
            tracking_reference=tracking_reference,
            received_at=now,
            interaction_mode=expected_mode,
            entry_count=len(entries),
        )

    @staticmethod
    async def _require_intake_authorization(
        session: AsyncSession, interaction: Interaction
    ) -> None:
        authorized = await session.scalar(
            select(ProcessingAuthorization.id)
            .join(
                ProcessingPurpose,
                ProcessingPurpose.id == ProcessingAuthorization.processing_purpose_id,
            )
            .join(
                ProcessingAuthorityType,
                ProcessingAuthorityType.id == ProcessingAuthorization.authority_type_id,
            )
            .where(
                ProcessingAuthorization.interaction_id == interaction.id,
                ProcessingPurpose.purpose_code == "PURP-01",
                ProcessingAuthorityType.authority_code
                == "VOLUNTARILY_PROVIDED_FOR_SPECIFIED_PURPOSE",
                ProcessingAuthorization.status == "ACTIVE",
            )
        )
        if authorized is None:
            raise AppException(
                403,
                "Intake acknowledgement required",
                "Continue after the intake notice before submitting information.",
                "https://api.sambal.gov.in/errors/intake-acknowledgement-required",
            )

    @staticmethod
    def _tracking_reference(year: int) -> str:
        return f"S-{year}-{secrets.token_hex(6).upper()}"

    async def _receipt_for_interaction(
        self,
        session: AsyncSession,
        interaction: Interaction,
        client_submission_id: str,
    ) -> IntakeSubmissionResponse:
        case = await session.scalar(select(Case).where(Case.id == interaction.case_id))
        if case is None:
            raise AppException(
                409,
                "Receipt unavailable",
                "The submission receipt is not available yet.",
                "https://api.sambal.gov.in/errors/receipt-unavailable",
            )
        entry_count = await session.scalar(
            select(func.count(CitizenIntakeEntry.id)).where(
                CitizenIntakeEntry.interaction_id == interaction.id,
                CitizenIntakeEntry.client_submission_id == client_submission_id,
            )
        )
        occurred_at = await session.scalar(
            select(func.max(InteractionEvent.occurred_at)).where(
                InteractionEvent.interaction_id == interaction.id,
                InteractionEvent.event_type == "CITIZEN_INTAKE_SUBMITTED",
            )
        )
        return IntakeSubmissionResponse(
            tracking_reference=case.public_tracking_id,
            received_at=occurred_at or case.created_at,
            interaction_mode=InteractionMode(interaction.interaction_mode),
            entry_count=int(entry_count or 0),
            case_created=False,
        )
