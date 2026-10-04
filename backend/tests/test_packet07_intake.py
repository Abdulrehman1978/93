"""Packet 07 citizen Write/Silent intake and Speak truth-boundary tests."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from pydantic import ValidationError
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.intake import intake_service
from app.channel.registry import InteractionMode
from app.channel.schemas import ChannelSessionCreate, ChannelSessionResponse
from app.channel.session import ChannelSessionService
from app.config import settings
from app.database import engine, get_db_session
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
    IntakeSubmissionResponse,
    SilentIntakeRequest,
    WriteIntakeRequest,
)
from app.intake.service import CitizenIntakeService
from app.main import app
from app.privacy.consent_engine import ConsentEngine
from app.security.encryption import (
    FieldEncryptor,
    authorized_field_decryption,
    use_field_encryptor,
)
from tests.test_packet06_channel import _acknowledge

pytestmark = pytest.mark.integration


class StaticKeyProvider:
    def current_key_id(self) -> str:
        return "PACKET07-TEST"

    def get_key(self, key_id: str) -> bytes:
        assert key_id == "PACKET07-TEST"
        return b"7" * 32

    def metadata(self) -> dict[str, str | bool]:
        return {"provider": "packet07-test", "external_secret_required": True}


@pytest.fixture
async def packet07_context() -> AsyncIterator[
    tuple[AsyncSession, ChannelSessionService, ConsentEngine, CitizenIntakeService]
]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            gateway = ChannelSessionService()
            encryptor = FieldEncryptor(StaticKeyProvider())
            with use_field_encryptor(encryptor):
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
    assert interaction.case_id is not None
    bound_event = await session.scalar(
        select(InteractionEvent.event_type).where(
            InteractionEvent.interaction_id == interaction.id,
            InteractionEvent.event_type == "CASE_BOUND",
        )
    )
    assert bound_event == "CASE_BOUND"
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
    for query in (
        "SELECT metadata::text FROM interaction_events WHERE interaction_id = :id",
        "SELECT safe_metadata::text FROM audit_events WHERE action = 'CITIZEN_INTAKE_SUBMITTED'",
        "SELECT reason FROM case_status_events WHERE case_id = :case_id",
        "SELECT payload_reference || COALESCE(payload_metadata::text, '') FROM async_jobs",
        "SELECT COALESCE(payload_reference, '') || COALESCE(payload_metadata::text, '') FROM integration_events",
    ):
        result = await session.execute(
            text(query),
            {"id": str(interaction.id), "case_id": str(interaction.case_id)},
        )
        assert all("safe way to ask" not in str(row[0]) for row in result)


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
    raw_contact = await session.scalar(
        text("SELECT contact_value FROM subject_contacts WHERE id = :id"),
        {"id": str(contact_row.id)},
    )
    assert request.optional_contact_value not in str(raw_contact)
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


async def test_completed_submission_retry_is_bounded(packet07_context) -> None:
    session, gateway, consent, intake = packet07_context
    created, interaction = await _authorized_session(
        session, gateway, consent, InteractionMode.TEXT
    )
    request = WriteIntakeRequest(client_submission_id="retry-window", narrative="retry safely")
    first = await intake.submit_write(session, created.session_id, created.session_token, request)
    immediate = await intake.submit_write(
        session, created.session_id, created.session_token, request
    )
    assert immediate.tracking_reference == first.tracking_reference

    now = datetime.now(UTC)
    interaction.started_at = now - timedelta(hours=1)
    interaction.ended_at = now - timedelta(seconds=10)
    inside = await intake.submit_write(session, created.session_id, created.session_token, request)
    assert inside.tracking_reference == first.tracking_reference

    interaction.ended_at = now - timedelta(seconds=settings.SUBMISSION_RECEIPT_RETRY_SECONDS + 1)
    with pytest.raises(AppException) as expired:
        await intake.submit_write(session, created.session_id, created.session_token, request)
    assert expired.value.status_code == 401


async def test_intake_rejects_missing_authorization_cross_session_token_and_expiry(
    packet07_context,
) -> None:
    session, gateway, consent, intake = packet07_context
    unauthenticated = await gateway.create(
        session,
        ChannelSessionCreate(
            interaction_mode=InteractionMode.TEXT,
            client_request_id=f"packet07-missing-{uuid.uuid4().hex[:16]}",
        ),
    )
    with pytest.raises(AppException) as missing_auth:
        await intake.submit_write(
            session,
            unauthenticated.session_id,
            unauthenticated.session_token,
            WriteIntakeRequest(client_submission_id="missing-auth", narrative="blocked"),
        )
    assert missing_auth.value.status_code == 403

    first, first_interaction = await _authorized_session(
        session, gateway, consent, InteractionMode.TEXT
    )
    second, _ = await _authorized_session(session, gateway, consent, InteractionMode.TEXT)
    with pytest.raises(AppException) as cross_session:
        await intake.submit_write(
            session,
            first.session_id,
            second.session_token,
            WriteIntakeRequest(client_submission_id="cross-session", narrative="blocked"),
        )
    assert cross_session.value.status_code == 401

    first_interaction.session_expires_at = datetime.now(UTC) - timedelta(seconds=1)
    with pytest.raises(AppException) as expired:
        await intake.submit_write(
            session,
            first.session_id,
            first.session_token,
            WriteIntakeRequest(client_submission_id="expired", narrative="blocked"),
        )
    assert expired.value.status_code == 401


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
    with pytest.raises(DBAPIError):
        await session.execute(
            text("DELETE FROM citizen_intake_entries WHERE id = :id"),
            {"id": str(entry_id)},
        )
    await session.rollback()


async def test_public_credential_and_intake_responses_are_no_store(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    class NoopDb:
        async def commit(self) -> None:
            return None

    async def fake_db():
        yield NoopDb()

    created = ChannelSessionResponse(
        session_id=uuid.uuid4(),
        session_token="test-token",
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
        channel="WEB",
        interaction_mode=InteractionMode.UNSELECTED,
        policy_version="packet-06-test",
        available_modes=(
            InteractionMode.UNSELECTED,
            InteractionMode.TEXT,
            InteractionMode.SILENT,
        ),
    )

    async def fake_create(_db, _request):
        return created

    async def fake_submit(_db, _session_id, _token, _request):
        return IntakeSubmissionResponse(
            tracking_reference="S-2099-TEST",
            received_at=datetime.now(UTC),
            interaction_mode=InteractionMode.TEXT,
            entry_count=1,
        )

    app.dependency_overrides[get_db_session] = fake_db
    monkeypatch.setattr("app.api.v1.channel.channel_session_service.create", fake_create)
    monkeypatch.setattr(intake_service, "submit_write", fake_submit)
    try:
        session_response = await client.post(
            "/api/v1/channel/sessions",
            json={"channel": "WEB", "interaction_mode": "UNSELECTED", "locale": "en"},
        )
        assert session_response.headers["cache-control"] == "no-store, max-age=0"
        assert session_response.headers["pragma"] == "no-cache"

        intake_response = await client.post(
            f"/api/v1/intake/sessions/{created.session_id}/write",
            headers={"X-Channel-Session-Token": created.session_token},
            json={"client_submission_id": "api-test", "narrative": "safe test"},
        )
        assert intake_response.headers["cache-control"] == "no-store, max-age=0"
        assert intake_response.headers["pragma"] == "no-cache"
    finally:
        app.dependency_overrides.pop(get_db_session, None)
