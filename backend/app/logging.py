"""Structured JSON Logging with PII Redaction and Correlation ID context.

Provides zero-leakage logging for citizen PII (phones, Aadhaar, emails)
and propagates request correlation IDs across async task boundaries.
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


def redact_pii(text: str) -> str:
    """Redact sensitive PII elements from log messages."""
    text = AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", text)
    text = INDIAN_PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
    text = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
    return text


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
            log_data["exception"] = self.formatException(record.exc_info)

        # Include custom extra attributes if present
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            for k, v in record.extra_fields.items():
                if isinstance(v, str):
                    log_data[k] = redact_pii(v)
                else:
                    log_data[k] = v

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
