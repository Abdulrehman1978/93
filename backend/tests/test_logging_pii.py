"""Unit tests for PII Redaction and Structured Logging."""

from app.logging import redact_pii


def test_redact_aadhaar():
    """Verify 12-digit Aadhaar numbers are redacted with or without spaces."""
    msg1 = "Complainant Aadhaar is 1234 5678 9012 registered."
    assert redact_pii(msg1) == "Complainant Aadhaar is [REDACTED_AADHAAR] registered."

    msg2 = "Aadhaar without space: 123456789012."
    assert redact_pii(msg2) == "Aadhaar without space: [REDACTED_AADHAAR]."


def test_redact_indian_phone():
    """Verify Indian mobile numbers with or without +91 are redacted."""
    msg1 = "Call back on +91-9876543210 urgently."
    assert redact_pii(msg1) == "Call back on [REDACTED_PHONE] urgently."

    msg2 = "Alternate phone is 9876543210."
    assert redact_pii(msg2) == "Alternate phone is [REDACTED_PHONE]."


def test_redact_email():
    """Verify email addresses are properly redacted."""
    msg = "Send report to victim.advocate@example.gov.in immediately."
    assert redact_pii(msg) == "Send report to [REDACTED_EMAIL] immediately."


def test_redact_mixed_text():
    """Verify multi-PII narratives are completely sanitized."""
    msg = "User 9876543210 with Aadhaar 9999 8888 7777 and email test@gov.in logged call."
    sanitized = redact_pii(msg)
    assert "[REDACTED_PHONE]" in sanitized
    assert "[REDACTED_AADHAAR]" in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert "9876543210" not in sanitized
    assert "9999 8888 7777" not in sanitized
    assert "test@gov.in" not in sanitized
