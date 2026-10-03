"""Structured JSON Logging with PII Redaction and Correlation ID context.

Provides baseline regex redaction for common identifiers (phone, Aadhaar, email)
with defensive structural sanitization and strict allowlisting of sensitive domains.
Regex redaction alone is not zero-leakage; high-risk citizen domains (narratives,
transcripts, raw inputs, identity docs) are omitted by policy.
"""

import datetime
import json
import logging
import re
from contextvars import ContextVar
from typing import Any

# ContextVar for request correlation tracking
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id_ctx", default="system")

# PII Regex Patterns for Redaction
AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
INDIAN_PHONE_PATTERN = re.compile(r"(?:\+91[-\s]?)?\b[6-9]\d{9}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
BEARER_TOKEN_PATTERN = re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+")
TOKEN_ASSIGNMENT_PATTERN = re.compile(r"(?i)(token\s*[=:]\s*)[^\s,;]+")

# Prohibited keys: citizen narratives, raw speech, credentials, identity docs
PROHIBITED_LOG_KEYS = {
    "transcript",
    "narrative",
    "citizen_narrative",
    "citizen_input",
    "raw_model_input",
    "raw_input",
    "address",
    "identity_document",
    "id_document",
    "request_body",
    "body",
    "password",
    "secret",
    "token",
    "authorization",
}


def redact_pii(text: str) -> str:
    """Redact sensitive PII elements from log messages."""
    text = BEARER_TOKEN_PATTERN.sub(r"\1[REDACTED_TOKEN]", text)
    text = TOKEN_ASSIGNMENT_PATTERN.sub(r"\1[REDACTED_TOKEN]", text)
    text = AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", text)
    text = INDIAN_PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
    text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    return text


def sanitize_structure(val: Any) -> Any:
    """Recursively sanitize nested dictionaries and lists, omitting prohibited keys."""
    if isinstance(val, dict):
        sanitized_dict: dict[str, Any] = {}
        for k, v in val.items():
            key_lower = str(k).lower().strip()
            if any(prohibited in key_lower for prohibited in PROHIBITED_LOG_KEYS):
                sanitized_dict[k] = "[PROHIBITED_SENSITIVE_FIELD_OMITTED]"
            else:
                sanitized_dict[k] = sanitize_structure(v)
        return sanitized_dict
    elif isinstance(val, list):
        return [sanitize_structure(item) for item in val]
    elif isinstance(val, str):
        return redact_pii(val)
    return val


class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as structured JSON with correlation IDs and PII redaction."""

    def format(self, record: logging.LogRecord) -> str:
        correlation_id = correlation_id_ctx.get()
        raw_message = record.getMessage()
        safe_message = redact_pii(raw_message)

        log_data: dict[str, Any] = {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "level": record.levelname,
            "message": safe_message,
            "correlation_id": correlation_id,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
        }

        if record.exc_info:
            raw_exc = self.formatException(record.exc_info)
            # Mask potential connection URI credentials before email regex
            masked_exc = re.sub(
                r"://([^:]+):([^@]+)@",
                r"://\1:[REDACTED_CREDENTIALS]@",
                raw_exc,
            )
            redacted_exc = redact_pii(masked_exc)
            log_data["exception"] = redacted_exc

        # Include custom extra attributes if present with deep sanitization
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            sanitized_extra = sanitize_structure(record.extra_fields)
            if isinstance(sanitized_extra, dict):
                log_data.update(sanitized_extra)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure root logger with structured JSON formatting."""
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(StructuredJsonFormatter())
    root_logger.addHandler(handler)

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return root_logger


logger = logging.getLogger("sambal")
