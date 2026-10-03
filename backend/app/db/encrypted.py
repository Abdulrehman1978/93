"""Reusable SQLAlchemy encrypted TEXT persistence adapter."""

from __future__ import annotations

from sqlalchemy import Text
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from app.security.encryption import decrypt_from_storage, encrypt_for_storage


class EncryptedText(TypeDecorator[str]):
    """Encrypt plaintext on bind and require authorized scope on result loading."""

    impl = Text
    cache_ok = True

    def __init__(self, field_name: str) -> None:
        super().__init__()
        self.field_name = field_name

    def process_bind_param(self, value: str | None, dialect: Dialect) -> str | None:
        del dialect
        if value is None:
            return None
        return encrypt_for_storage(value, field_name=self.field_name)

    def process_result_value(self, value: str | None, dialect: Dialect) -> str | None:
        del dialect
        if value is None:
            return None
        return decrypt_from_storage(value, field_name=self.field_name)

    def copy(self, **kw: object) -> EncryptedText:
        del kw
        return EncryptedText(self.field_name)
