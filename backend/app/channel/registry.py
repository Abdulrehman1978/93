"""Provider-neutral channel registry and capability truth."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ChannelType(StrEnum):
    WEB = "WEB"
    PORTAL = "PORTAL"
    IVR = "IVR"
    TELEPHONY = "TELEPHONY"
    CHATBOT = "CHATBOT"
    MOBILE = "MOBILE"
    OPERATOR = "OPERATOR"
    SYSTEM = "SYSTEM"


class InteractionMode(StrEnum):
    UNSELECTED = "UNSELECTED"
    VOICE = "VOICE"
    TEXT = "TEXT"
    SILENT = "SILENT"


class CapabilityStatus(StrEnum):
    LIVE_TESTED = "LIVE_TESTED"
    ADAPTER_READY = "ADAPTER_READY"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    DISABLED = "DISABLED"


@dataclass(frozen=True, slots=True)
class ChannelCapability:
    channel: ChannelType
    status: CapabilityStatus
    supported_modes: tuple[InteractionMode, ...]
    provider_code: str | None
    public_entrypoint: bool
    human_review_required: bool
    note: str


_CAPABILITIES: dict[ChannelType, ChannelCapability] = {
    ChannelType.WEB: ChannelCapability(
        ChannelType.WEB,
        CapabilityStatus.LIVE_TESTED,
        (InteractionMode.UNSELECTED, InteractionMode.TEXT),
        None,
        True,
        False,
        "Canonical public session entrypoint; no external provider is called.",
    ),
    ChannelType.PORTAL: ChannelCapability(
        ChannelType.PORTAL,
        CapabilityStatus.ADAPTER_READY,
        tuple(InteractionMode),
        None,
        False,
        False,
        "Adapter boundary reserved for authenticated portal integration.",
    ),
    ChannelType.IVR: ChannelCapability(
        ChannelType.IVR,
        CapabilityStatus.NOT_CONFIGURED,
        (InteractionMode.VOICE,),
        None,
        False,
        True,
        "No telephony provider is configured.",
    ),
    ChannelType.TELEPHONY: ChannelCapability(
        ChannelType.TELEPHONY,
        CapabilityStatus.NOT_CONFIGURED,
        (InteractionMode.VOICE,),
        None,
        False,
        True,
        "No telephony provider is configured.",
    ),
    ChannelType.CHATBOT: ChannelCapability(
        ChannelType.CHATBOT,
        CapabilityStatus.NOT_CONFIGURED,
        (InteractionMode.TEXT,),
        None,
        False,
        False,
        "No chatbot provider is configured.",
    ),
    ChannelType.MOBILE: ChannelCapability(
        ChannelType.MOBILE,
        CapabilityStatus.NOT_CONFIGURED,
        tuple(InteractionMode),
        None,
        False,
        False,
        "No mobile provider is configured.",
    ),
    ChannelType.OPERATOR: ChannelCapability(
        ChannelType.OPERATOR,
        CapabilityStatus.ADAPTER_READY,
        tuple(InteractionMode),
        None,
        False,
        True,
        "Operator-originated records require an authenticated human boundary.",
    ),
    ChannelType.SYSTEM: ChannelCapability(
        ChannelType.SYSTEM,
        CapabilityStatus.ADAPTER_READY,
        tuple(InteractionMode),
        None,
        False,
        True,
        "System provenance is internal only and never a public channel.",
    ),
}


def get_channel_capability(channel: ChannelType) -> ChannelCapability:
    return _CAPABILITIES[channel]


def all_channel_capabilities() -> tuple[ChannelCapability, ...]:
    return tuple(_CAPABILITIES.values())
