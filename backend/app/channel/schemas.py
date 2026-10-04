"""Public channel gateway request and response contracts."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.channel.registry import CapabilityStatus, ChannelType, InteractionMode


class ConsentChoice(StrEnum):
    GRANTED = "GRANTED"
    DECLINED = "DECLINED"
    REVOKED = "REVOKED"


class TranslationTruthStatus(StrEnum):
    AUTHORITATIVE = "AUTHORITATIVE"
    HUMAN_VERIFIED = "HUMAN_VERIFIED"
    MACHINE_TRANSLATED = "MACHINE_TRANSLATED"
    FALLBACK_LANGUAGE = "FALLBACK_LANGUAGE"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class ConsentMode(StrEnum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    NOT_REQUIRED = "NOT_REQUIRED"
    PROHIBITED_WITHOUT_HUMAN_AUTHORIZATION = "PROHIBITED_WITHOUT_HUMAN_AUTHORIZATION"


class ChannelSessionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    channel: ChannelType = ChannelType.WEB
    interaction_mode: InteractionMode = InteractionMode.UNSELECTED
    locale: str = Field(default="en", min_length=2, max_length=20, pattern=r"^[A-Za-z-]+$")
    client_request_id: str | None = Field(
        default=None, min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]{1,80}$"
    )


class ChannelSessionResponse(BaseModel):
    session_id: uuid.UUID
    session_token: str
    expires_at: datetime
    channel: ChannelType
    interaction_mode: InteractionMode
    policy_version: str
    available_modes: tuple[InteractionMode, ...]


class SessionStateResponse(BaseModel):
    session_id: uuid.UUID
    channel: ChannelType
    interaction_mode: InteractionMode
    status: str
    language: str | None
    expires_at: datetime | None
    last_activity_at: datetime | None
    policy_version: str | None
    intake_ready: bool


class ChannelCapabilityResponse(BaseModel):
    channel: ChannelType
    status: CapabilityStatus
    supported_modes: tuple[InteractionMode, ...]
    provider_code: str | None
    public_entrypoint: bool
    human_review_required: bool
    note: str


class ConsentRequirement(BaseModel):
    purpose_code: str
    name: str
    lawful_basis: str
    allowed_lawful_authorities: tuple[str, ...] = ()
    applicable_modes: tuple[InteractionMode, ...] = ()
    consent_mode: ConsentMode
    notice_required: bool
    notice_version: str
    can_decline: bool
    effect_of_decline: str
    can_revoke: bool
    human_approval_required: bool
    why_needed: str
    data_categories: tuple[str, ...]
    recipients: tuple[str, ...]
    retention_status: str


class SessionPolicyResponse(BaseModel):
    policy_version: str
    requested_locale: str
    served_locale: str
    translation_status: TranslationTruthStatus
    required_notices: tuple[ConsentRequirement, ...]
    optional_consents: tuple[ConsentRequirement, ...]
    available_alternatives: tuple[str, ...]
    current_decisions: dict[str, ConsentChoice]
    capabilities: tuple[ChannelCapabilityResponse, ...]
    conditional_consents: tuple[ConsentRequirement, ...] = ()
    intake_ready: bool = False


class ConsentDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    purpose_code: str = Field(min_length=1, max_length=50, pattern=r"^[A-Z0-9-]+$")
    choice: ConsentChoice
    policy_version: str = Field(min_length=1, max_length=80)
    client_action_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]{1,80}$")


class IntakeAcknowledgementRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_version: str = Field(min_length=1, max_length=80)
    client_action_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]{1,80}$")


class ConsentReceipt(BaseModel):
    consent_event_id: uuid.UUID
    purpose_code: str
    choice: ConsentChoice
    policy_version: str
    recorded_at: datetime
    current_processing_authorized: bool


class ModeSelectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interaction_mode: InteractionMode


class SessionControlResponse(BaseModel):
    session_id: uuid.UUID
    status: str
    interaction_mode: InteractionMode
