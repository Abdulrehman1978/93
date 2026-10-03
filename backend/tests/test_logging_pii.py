"""Unit tests for PII Redaction, Nested Sanitization, and Prohibited Log Fields."""

import json
import logging

from app.logging import StructuredJsonFormatter, redact_pii


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


def test_nested_structured_logging_pii_sanitization():
    """Verify nested structured fields in extra_fields are recursively sanitized."""
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        name="sambal.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Nested telemetry event",
        args=(),
        exc_info=None,
    )
    record.extra_fields = {
        "user_context": {
            "contact": {
                "phone": "+91 9876543210",
                "email": "victim_contact@domain.gov.in",
            },
            "history": ["Call from 9876543210", "Aadhaar verified: 1234 5678 9012"],
        }
    }

    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert "9876543210" not in formatted
    assert "victim_contact@domain.gov.in" not in formatted
    assert "1234 5678 9012" not in formatted
    assert parsed["user_context"]["contact"]["phone"] == "[REDACTED_PHONE]"
    assert parsed["user_context"]["contact"]["email"] == "[REDACTED_EMAIL]"
    assert parsed["user_context"]["history"][0] == "Call from [REDACTED_PHONE]"
    assert parsed["user_context"]["history"][1] == "Aadhaar verified: [REDACTED_AADHAAR]"


def test_prohibited_log_fields_omitted_by_policy():
    """Verify prohibited fields like transcripts, narratives, and raw input are omitted by policy."""
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        name="sambal.test",
        level=logging.WARNING,
        pathname=__file__,
        lineno=20,
        msg="Prohibited data audit event",
        args=(),
        exc_info=None,
    )
    record.extra_fields = {
        "transcript": "Complainant said the village sarpanch assaulted her family",
        "citizen_narrative": "Detailed narrative of atrocities at residence",
        "raw_model_input": [0.12, 0.45, 0.98, "raw_audio_stream"],
        "identity_document": "Voter ID ABC1234567",
        "password": "plaintext_user_password",
        "secret": "confidential_api_token",
    }

    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert "village sarpanch assaulted" not in formatted
    assert "Detailed narrative of atrocities" not in formatted
    assert "raw_audio_stream" not in formatted
    assert "plaintext_user_password" not in formatted

    assert parsed["transcript"] == "[PROHIBITED_SENSITIVE_FIELD_OMITTED]"
    assert parsed["citizen_narrative"] == "[PROHIBITED_SENSITIVE_FIELD_OMITTED]"
    assert parsed["raw_model_input"] == "[PROHIBITED_SENSITIVE_FIELD_OMITTED]"
    assert parsed["identity_document"] == "[PROHIBITED_SENSITIVE_FIELD_OMITTED]"
    assert parsed["password"] == "[PROHIBITED_SENSITIVE_FIELD_OMITTED]"
    assert parsed["secret"] == "[PROHIBITED_SENSITIVE_FIELD_OMITTED]"


def test_exception_pii_and_credential_sanitization():
    """Verify exceptions formatted into logs have PII and database passwords redacted."""
    formatter = StructuredJsonFormatter()
    try:
        raise ValueError(
            "Connection failed to postgresql+asyncpg://sambal_user:LEAKY_SECRET_PASS@db.internal:5432/db "
            "for user phone +91 9876543210"
        )
    except Exception:
        import sys

        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="sambal.test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=30,
        msg="Database operation failed",
        args=(),
        exc_info=exc_info,
    )

    formatted = formatter.format(record)
    assert "LEAKY_SECRET_PASS" not in formatted
    assert "9876543210" not in formatted
    assert "[REDACTED_CREDENTIALS]" in formatted
    assert "[REDACTED_PHONE]" in formatted
