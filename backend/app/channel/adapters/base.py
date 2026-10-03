"""Small adapter interface; provider SDKs must remain outside the domain core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.channel.registry import ChannelCapability, ChannelType


@dataclass(frozen=True, slots=True)
class NormalizedChannelEvent:
    event_type: str
    source_reference: str | None
    safe_metadata: dict[str, str]


class ChannelAdapter(Protocol):
    channel: ChannelType

    def capabilities(self) -> ChannelCapability: ...

    def validate_source(self, source_reference: str | None) -> None: ...

    def normalize_event(
        self, event_type: str, source_reference: str | None, metadata: dict[str, str] | None
    ) -> NormalizedChannelEvent: ...
