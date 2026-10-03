"""Canonical first-party web adapter."""

from __future__ import annotations

from app.channel.adapters.base import NormalizedChannelEvent
from app.channel.registry import ChannelCapability, ChannelType, get_channel_capability
from app.errors import AppException


class WebChannelAdapter:
    channel = ChannelType.WEB

    def capabilities(self) -> ChannelCapability:
        return get_channel_capability(self.channel)

    def validate_source(self, source_reference: str | None) -> None:
        if source_reference is not None and len(source_reference) > 255:
            raise AppException(400, "Invalid channel event", "The event reference is invalid.")

    def normalize_event(
        self, event_type: str, source_reference: str | None, metadata: dict[str, str] | None
    ) -> NormalizedChannelEvent:
        self.validate_source(source_reference)
        safe_metadata = metadata or {}
        return NormalizedChannelEvent(event_type, source_reference, dict(safe_metadata))
