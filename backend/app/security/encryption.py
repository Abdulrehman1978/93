"""Application-level authenticated encryption for highly sensitive fields."""

from __future__ import annotations

import base64
import binascii
import json
import secrets
from dataclasses import dataclass
from typing import Protocol

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


class EncryptionError(Exception):
    """Base error that never includes plaintext or key material."""


class KeyProvider(Protocol):
    """Provider boundary for KMS/HSM/Vault/secure mounted secret implementations."""

    def current_key_id(self) -> str: ...

    def get_key(self, key_id: str) -> bytes: ...

    def metadata(self) -> dict[str, str | bool]: ...


def _decode_key(value: str) -> bytes:
    try:
        decoded = base64.urlsafe_b64decode(value.encode("ascii"))
    except (ValueError, UnicodeError, binascii.Error) as exc:
        raise EncryptionError("invalid encryption key encoding") from exc
    if len(decoded) != 32:
        raise EncryptionError("AES-256 key material must be exactly 32 bytes")
    return decoded


@dataclass(frozen=True, slots=True)
class EnvironmentKeyProvider:
    """Reads versioned keys from deployment secrets, never from domain rows."""

    current_id: str
    keys: dict[str, bytes]

    @classmethod
    def from_settings(cls) -> EnvironmentKeyProvider:
        keys: dict[str, bytes] = {}
        if settings.FIELD_ENCRYPTION_KEYS_JSON:
            try:
                raw_keys = json.loads(settings.FIELD_ENCRYPTION_KEYS_JSON)
            except json.JSONDecodeError as exc:
                raise EncryptionError("invalid versioned encryption key configuration") from exc
            if not isinstance(raw_keys, dict):
                raise EncryptionError("versioned encryption keys must be an object")
            for key_id, value in raw_keys.items():
                if not isinstance(key_id, str) or not isinstance(value, str):
                    raise EncryptionError("versioned encryption key entries are invalid")
                keys[key_id] = _decode_key(value)
        if settings.FIELD_ENCRYPTION_KEY:
            keys[settings.FIELD_ENCRYPTION_KEY_ID] = _decode_key(settings.FIELD_ENCRYPTION_KEY)
        if settings.ENVIRONMENT in ("staging", "production") and not keys:
            raise EncryptionError("production encryption key material is not configured")
        if not keys:
            raise EncryptionError("encryption key material is not configured")
        if settings.FIELD_ENCRYPTION_KEY_ID not in keys:
            raise EncryptionError("current encryption key id is not present")
        return cls(current_id=settings.FIELD_ENCRYPTION_KEY_ID, keys=keys)

    def current_key_id(self) -> str:
        return self.current_id

    def get_key(self, key_id: str) -> bytes:
        try:
            return self.keys[key_id]
        except KeyError as exc:
            raise EncryptionError("encryption key version is unavailable") from exc

    def metadata(self) -> dict[str, str | bool]:
        return {"provider": "environment-secret-boundary", "external_secret_required": True}


class FieldEncryptor:
    """AES-256-GCM envelope codec with field-bound associated data."""

    VERSION = 1
    ALGORITHM = "AES-256-GCM"

    def __init__(self, key_provider: KeyProvider) -> None:
        self.key_provider = key_provider

    def encrypt(self, plaintext: str, *, field_name: str) -> str:
        if not isinstance(plaintext, str):
            raise EncryptionError("only text fields may be encrypted")
        nonce = secrets.token_bytes(12)
        key_id = self.key_provider.current_key_id()
        aad = field_name.encode("utf-8")
        ciphertext = AESGCM(self.key_provider.get_key(key_id)).encrypt(
            nonce, plaintext.encode("utf-8"), aad
        )
        envelope = {
            "version": self.VERSION,
            "algorithm": self.ALGORITHM,
            "key_id": key_id,
            "nonce": base64.urlsafe_b64encode(nonce).decode("ascii"),
            "ciphertext": base64.urlsafe_b64encode(ciphertext).decode("ascii"),
        }
        return json.dumps(envelope, separators=(",", ":"), sort_keys=True)

    def decrypt(self, envelope_text: str, *, field_name: str) -> str:
        try:
            envelope = json.loads(envelope_text)
            if (
                envelope.get("version") != self.VERSION
                or envelope.get("algorithm") != self.ALGORITHM
                or not isinstance(envelope.get("key_id"), str)
                or not isinstance(envelope.get("nonce"), str)
                or not isinstance(envelope.get("ciphertext"), str)
            ):
                raise EncryptionError("unsupported encrypted field envelope")
            nonce = base64.urlsafe_b64decode(envelope["nonce"].encode("ascii"))
            ciphertext = base64.urlsafe_b64decode(envelope["ciphertext"].encode("ascii"))
            plaintext = AESGCM(self.key_provider.get_key(envelope["key_id"])).decrypt(
                nonce, ciphertext, field_name.encode("utf-8")
            )
            return plaintext.decode("utf-8")
        except (KeyError, TypeError, ValueError, UnicodeError, binascii.Error, InvalidTag) as exc:
            raise EncryptionError("encrypted field authentication failed") from exc

    def reencrypt(self, envelope_text: str, *, field_name: str) -> str:
        return self.encrypt(
            self.decrypt(envelope_text, field_name=field_name), field_name=field_name
        )
