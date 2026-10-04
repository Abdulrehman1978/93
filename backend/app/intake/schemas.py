"""Strict public contracts for the Packet 07 citizen intake boundary."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator

from app.channel.registry import InteractionMode


class CurrentSafetyChoice(StrEnum):
    YES = "YES"
    NO_SOMEONE_MAY_BE_NEARBY = "NO_SOMEONE_MAY_BE_NEARBY"
    NOT_SURE = "NOT_SURE"
    SKIP = "SKIP"


class UrgentHelpChoice(StrEnum):
    YES_AS_SOON_AS_POSSIBLE = "YES_AS_SOON_AS_POSSIBLE"
    NO = "NO"
    NOT_SURE = "NOT_SURE"
    SKIP = "SKIP"


class ContactPreference(StrEnum):
    DO_NOT_CALL = "DO_NOT_CALL"
    SILENT_SMS_PREFERRED = "SILENT_SMS_PREFERRED"
    WHATSAPP_PREFERRED = "WHATSAPP_PREFERRED"
    ASK_ME_LATER = "ASK_ME_LATER"
    NO_CONTACT_DETAILS_NOW = "NO_CONTACT_DETAILS_NOW"


def _reject_nul(value: str | None, field_name: str) -> str | None:
    if value is not None and "\x00" in value:
        raise ValueError(f"{field_name} contains an invalid control character")
    return value


class WriteIntakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_submission_id: str = Field(
        min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]{1,80}$"
    )
    narrative: str = Field(min_length=1, max_length=16_000)
    optional_when: str | None = Field(default=None, max_length=160)
    optional_location: str | None = Field(default=None, max_length=300)
    optional_current_safety: CurrentSafetyChoice | None = None
    optional_contact_preference: ContactPreference | None = None
    optional_contact_value: str | None = Field(default=None, min_length=1, max_length=320)

    @field_validator("narrative")
    @classmethod
    def narrative_must_contain_words(cls, value: str) -> str:
        _reject_nul(value, "narrative")
        if not value.strip():
            raise ValueError("Please share a few words about what happened.")
        return value

    @field_validator("optional_when", "optional_location")
    @classmethod
    def optional_text_must_be_safe(cls, value: str | None, info: ValidationInfo) -> str | None:
        return _reject_nul(value, info.field_name or "optional_text")

    @field_validator("optional_contact_value")
    @classmethod
    def contact_value_must_be_single_line(cls, value: str | None) -> str | None:
        _reject_nul(value, "optional_contact_value")
        if value is not None and any(character in value for character in "\r\n"):
            raise ValueError("Contact details must be entered on one line.")
        return value

    @model_validator(mode="after")
    def validate_contact_pair(self) -> WriteIntakeRequest:
        if self.optional_contact_value and self.optional_contact_preference in {
            None,
            ContactPreference.DO_NOT_CALL,
            ContactPreference.NO_CONTACT_DETAILS_NOW,
        }:
            raise ValueError("Choose a safe contact preference before adding contact details.")
        return self


class SilentIntakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_submission_id: str = Field(
        min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._:-]{1,80}$"
    )
    current_safety: CurrentSafetyChoice
    urgent_help: UrgentHelpChoice
    contact_preference: ContactPreference
    optional_contact_value: str | None = Field(default=None, min_length=1, max_length=320)

    @field_validator("optional_contact_value")
    @classmethod
    def contact_value_must_be_single_line(cls, value: str | None) -> str | None:
        _reject_nul(value, "optional_contact_value")
        if value is not None and any(character in value for character in "\r\n"):
            raise ValueError("Contact details must be entered on one line.")
        return value

    @model_validator(mode="after")
    def validate_contact_pair(self) -> SilentIntakeRequest:
        if self.optional_contact_value and self.contact_preference in {
            ContactPreference.DO_NOT_CALL,
            ContactPreference.NO_CONTACT_DETAILS_NOW,
        }:
            raise ValueError("Choose a contact preference before adding contact details.")
        return self


class IntakeSubmissionResponse(BaseModel):
    tracking_reference: str
    received_at: datetime
    interaction_mode: InteractionMode
    entry_count: int = Field(ge=1)
    case_created: bool = True
