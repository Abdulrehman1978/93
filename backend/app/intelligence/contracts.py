"""Abstract Intelligence Provider Boundaries for SAMBAL.

Strict Architecture Rule:
Business and domain logic must NEVER directly import or depend on a specific external
model SDK (e.g. OpenAI, Anthropic, HuggingFace, CTranslate2, Google GenAI).
All intelligence capabilities are accessed exclusively via these provider protocols.

Implementation candidates (such as faster-whisper-turbo CTranslate2 INT8 as BASELINE_CANDIDATE)
must implement these abstract contracts behind modular adapter boundaries.
"""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class AudioChunk:
    """Represents a discrete raw PCM or audio segment for streaming or batch analysis."""

    sample_rate: int
    channels: int
    data: bytes
    timestamp_ms: int
    duration_ms: int


@dataclass(frozen=True)
class ASRTranscriptSegment:
    """Streaming or final transcription segment produced by an ASRProvider."""

    start_ms: int
    end_ms: int
    text: str
    language: str
    confidence: float
    is_final: bool


@dataclass(frozen=True)
class SafetyAlertSignal:
    """Immediate safety or distress alert candidate detected by safety providers."""

    signal_id: str
    category: str
    severity: str
    snippet: str
    confidence: float
    timestamp_ms: int


@runtime_checkable
class ASRProvider(Protocol):
    """Abstract contract for Automatic Speech Recognition.

    Current baseline candidate: faster-whisper-turbo + CTranslate2 INT8 (BASELINE_CANDIDATE).
    Benchmarked in Packet 08 against Indic-focused/government alternatives (e.g. IndicConformer/Bhashini).
    """

    async def transcribe_stream(self, chunk: AudioChunk) -> list[ASRTranscriptSegment]:
        """Process incoming streaming audio chunk and return partial/stable segments."""
        ...

    async def transcribe_file(
        self, audio_bytes: bytes, language: str | None = None
    ) -> list[ASRTranscriptSegment]:
        """Process complete audio recording in batch."""
        ...


@runtime_checkable
class LanguageDetectionProvider(Protocol):
    """Abstract contract for spoken and text language identification."""

    async def detect_language_audio(self, chunk: AudioChunk) -> tuple[str, float]:
        """Detect language code (e.g., 'hi', 'en', 'mr') and confidence from audio."""
        ...

    async def detect_language_text(self, text: str) -> tuple[str, float]:
        """Detect language code and confidence from text snippet."""
        ...


@runtime_checkable
class TranslationProvider(Protocol):
    """Abstract contract for Indic-to-English and cross-Indic translation."""

    async def translate_to_english(self, text: str, source_language: str) -> str:
        """Translate source text to normalized English for downstream processing."""
        ...


@runtime_checkable
class TextSafetyProvider(Protocol):
    """Abstract contract for immediate distress/danger phrase detection in transcripts."""

    async def evaluate_text_safety(self, text: str, language: str) -> list[SafetyAlertSignal]:
        """Detect acute distress keywords, coercion hints, or immediate danger signals."""
        ...


@runtime_checkable
class ContextExtractionProvider(Protocol):
    """Abstract contract for extracting reported facts, entities, and urgency indicators."""

    async def extract_entities(self, text: str) -> dict[str, Any]:
        """Extract structured entities (e.g. location, incident nature, dates)."""
        ...


@runtime_checkable
class AcousticFeatureProvider(Protocol):
    """Abstract contract for non-semantic acoustic analysis (pitch, jitter, SNR, pauses)."""

    async def extract_features(self, chunk: AudioChunk) -> dict[str, float]:
        """Compute acoustic parameters such as pitch perturbation, shimmer, energy variance."""
        ...


@runtime_checkable
class AffectiveSignalProvider(Protocol):
    """Abstract contract for detecting voice distress or tremor indicators."""

    async def analyze_affect(self, chunk: AudioChunk) -> dict[str, float]:
        """Assess acoustic distress indicators without making diagnostic claims."""
        ...


@runtime_checkable
class LLMProvider(Protocol):
    """Abstract contract for generative summary, grounding, and operator copilot suggestions."""

    async def generate_completion(
        self, prompt: str, system_prompt: str | None = None, temperature: float = 0.2
    ) -> str:
        """Generate structured completion adhering to trauma-informed prompt templates."""
        ...
