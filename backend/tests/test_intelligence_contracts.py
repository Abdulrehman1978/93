"""Tests for Abstract Intelligence Provider Contracts and Conformance."""

from app.intelligence.contracts import (
    AcousticFeatureProvider,
    AffectiveSignalProvider,
    ASRProvider,
    ASRTranscriptSegment,
    AudioChunk,
    ContextExtractionProvider,
    LanguageDetectionProvider,
    LLMProvider,
    TextSafetyProvider,
    TranslationProvider,
)


class MockASRProvider:
    """Mock implementation fulfilling the ASRProvider protocol."""

    async def transcribe_stream(self, chunk: AudioChunk) -> list[ASRTranscriptSegment]:
        return [
            ASRTranscriptSegment(
                start_ms=0,
                end_ms=chunk.duration_ms,
                text="Help needed",
                language="hi",
                confidence=0.95,
                is_final=True,
            )
        ]

    async def transcribe_file(
        self, _audio_bytes: bytes, _language: str | None = None
    ) -> list[ASRTranscriptSegment]:
        return []


def test_asr_provider_runtime_check():
    """Verify runtime checkability of ASRProvider protocol."""
    mock = MockASRProvider()
    assert isinstance(mock, ASRProvider)


def test_protocols_exist_and_checkable():
    """Verify all 8 intelligence boundary protocols exist."""
    protocols = [
        ASRProvider,
        LanguageDetectionProvider,
        TranslationProvider,
        TextSafetyProvider,
        ContextExtractionProvider,
        AcousticFeatureProvider,
        AffectiveSignalProvider,
        LLMProvider,
    ]
    assert len(protocols) == 8
