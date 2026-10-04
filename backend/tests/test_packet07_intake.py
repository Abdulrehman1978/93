"""Packet 07 citizen Write/Silent intake and Speak truth-boundary tests."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.channel.registry import InteractionMode
from app.channel.schemas import ChannelSessionCreate
from app.channel.session import ChannelSessionService
from app.database import engine
from app.db.models.casework import (
    Case,
    CitizenIntakeEntry,
    Interaction,
    InteractionEvent,
    SubjectContact,
)
from app.db.models.platform import AuditEvent
from app.errors import AppException
from app.intake.schemas import (
    ContactPreference,
    CurrentSafetyChoice,
    SilentIntakeRequest,
    WriteIntakeRequest,
)
from app.intake.service import CitizenIntakeService
from app.privacy.consent_engine import ConsentEngine
from app.security.encryption import authorized_field_decryption
from tests.test_packet06_channel import _acknowledge

pytestmark = pytest.mark.integration


@pytest.fixture
async def packet07_context() -> AsyncIterator[
    tuple[AsyncSession, ChannelSessionService, ConsentEngine, CitizenIntakeService]
]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            gateway = ChannelSessionService()
            yield session, gateway, ConsentEngine(gateway), CitizenIntakeService(gateway)
        finally:
            await session.close()
            await transaction.rollback()
            await engine.dispose()


async def _authorized_session(
    session: AsyncSession,
    gateway: ChannelSessionService,
    consent: ConsentEngine,
    mode: InteractionMode,
):
    created = await gateway.create(
        session,
        ChannelSessionCreate(
            interaction_mode=mode, client_request_id=f"packet07-{uuid.uuid4().hex[:16]}"
        ),
    )
    interaction = await session.get(Interaction, created.session_id)
    assert interaction is not None
    await _acknowledge(session, consent, created, interaction)
    return created, interaction


def test_packet07_contracts_reject_extra_fields_and_unsafe_values() -> None:
    with pytest.raises(ValidationError):
        WriteIntakeRequest(client_submission_id="write-1", narrative="hello", case_id="forged")
    with pytest.raises(ValidationError):
        WriteIntakeRequest(client_submission_id="write-1", narrative="\x00secret")
    with pytest.raises(ValidationError):
        SilentIntakeRequest(
            client_submission_id="silent-1",
            current_safety=CurrentSafetyChoice.YES,
            urgent_help="NO",
            contact_preference=ContactPreference.DO_NOT_CALL,
            optional_contact_value="+91 90000 00000",
        )


async def test_write_is_atomic_encrypted_and_idempotent(packet07_context) -> None:
    session, gateway, consent, intake = packet07_context
    created, interaction = await _authorized_session(
        session, gateway, consent, InteractionMode.TEXT
    )
    request = WriteIntakeRequest(
        client_submission_id="write-submit-1", narrative="I need a safe way to ask for help."
    )
    first = await intake.submit_write(session, created.session_id, created.session_token, request)
    second = await intake.submit_write(session, created.session_id, created.session_token, request)
    assert first.tracking_reference == second.tracking_reference
    assert second.case_created is False
    assert (
        await session.scalar(
            select(func.count(Case.id)).where(Case.subject_id == interaction.subject_id)
        )
        == 1
    )
    raw = await session.scalar(
        text("SELECT content FROM citizen_intake_entries WHERE interaction_id = :id"),
        {"id": str(interaction.id)},
    )
    assert raw is not None
    assert "safe way to ask" not in str(raw)
    with authorized_field_decryption("citizen_intake_entries.content"):
        stored = await session.scalar(
            select(CitizenIntakeEntry.content).where(
                CitizenIntakeEntry.interaction_id == interaction.id
            )
        )
    assert stored == request.narrative
    event = await session.scalar(
        select(InteractionEvent.event_metadata).where(
            InteractionEvent.interaction_id == interaction.id,
            InteractionEvent.event_type == "CITIZEN_INTAKE_SUBMITTED",
        )
    )
    assert event == {"interaction_mode": "TEXT", "entry_count": 1}
    audit = await session.scalar(
        select(AuditEvent.safe_metadata).where(AuditEvent.action == "CITIZEN_INTAKE_SUBMITTED")
    )
    assert "safe way to ask" not in str(audit)


async def test_silent_contact_is_encrypted_and_not_safe_to_use_by_default(packet07_context) -> None:
    session, gateway, consent, intake = packet07_context
    created, interaction = await _authorized_session(
        session, gateway, consent, InteractionMode.SILENT
    )
    request = SilentIntakeRequest(
        client_submission_id="silent-submit-1",
        current_safety=CurrentSafetyChoice.NOT_SURE,
        urgent_help="YES_AS_SOON_AS_POSSIBLE",
        contact_preference=ContactPreference.SILENT_SMS_PREFERRED,
        optional_contact_value="+91 90000 00000",
    )
    response = await intake.submit_silent(
        session, created.session_id, created.session_token, request
    )
    assert response.interaction_mode is InteractionMode.SILENT
    contact = await session.execute(
        select(SubjectContact.id, SubjectContact.safe_to_use).where(
            SubjectContact.subject_id == interaction.subject_id
        )
    )
    contact_row = contact.one()
    assert contact_row.safe_to_use is False
    with authorized_field_decryption("subject_contacts.contact_value"):
        stored_contact = await session.scalar(
            select(SubjectContact.contact_value).where(SubjectContact.id == contact_row.id)
        )
    assert stored_contact == request.optional_contact_value


async def test_completed_session_rejects_different_submission_and_wrong_mode(
    packet07_context,
) -> None:
    session, gateway, consent, intake = packet07_context
    created, _ = await _authorized_session(session, gateway, consent, InteractionMode.TEXT)
    await intake.submit_write(
        session,
        created.session_id,
        created.session_token,
        WriteIntakeRequest(client_submission_id="write-submit-2", narrative="first"),
    )
    with pytest.raises(AppException) as different:
        await intake.submit_write(
            session,
            created.session_id,
            created.session_token,
            WriteIntakeRequest(client_submission_id="write-submit-3", narrative="second"),
        )
    assert different.value.status_code == 409
    silent_created, _ = await _authorized_session(session, gateway, consent, InteractionMode.TEXT)
    with pytest.raises(AppException) as mismatch:
        await intake.submit_silent(
            session,
            silent_created.session_id,
            silent_created.session_token,
            SilentIntakeRequest(
                client_submission_id="silent-wrong-mode",
                current_safety="YES",
                urgent_help="NO",
                contact_preference="NO_CONTACT_DETAILS_NOW",
            ),
        )
    assert mismatch.value.status_code == 409


async def test_intake_entries_are_append_only(packet07_context) -> None:
    session, gateway, consent, intake = packet07_context
    created, interaction = await _authorized_session(
        session, gateway, consent, InteractionMode.TEXT
    )
    await intake.submit_write(
        session,
        created.session_id,
        created.session_token,
        WriteIntakeRequest(client_submission_id="append-only-1", narrative="append only"),
    )
    entry_id = await session.scalar(
        select(CitizenIntakeEntry.id).where(CitizenIntakeEntry.interaction_id == interaction.id)
    )
    with pytest.raises(DBAPIError):
        await session.execute(
            text("UPDATE citizen_intake_entries SET question_code = 'TAMPERED' WHERE id = :id"),
            {"id": str(entry_id)},
        )
    await session.rollback()
