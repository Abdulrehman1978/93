"""Packet 04 token-verification and field-encryption security tests."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app.security.encryption import EncryptionError, FieldEncryptor
from app.security.identity import OIDCIdentityProvider, TokenValidationError


class StaticKeyProvider:
    def __init__(self, keys: dict[str, bytes], current: str) -> None:
        self.keys = keys
        self.current = current

    def current_key_id(self) -> str:
        return self.current

    def get_key(self, key_id: str) -> bytes:
        return self.keys[key_id]

    def metadata(self) -> dict[str, str | bool]:
        return {"provider": "test", "external_secret_required": True}


def test_field_encryption_is_authenticated_versioned_and_rotatable() -> None:
    old_key = b"1" * 32
    new_key = b"2" * 32
    old = FieldEncryptor(StaticKeyProvider({"KEY-V1": old_key}, "KEY-V1"))
    rotated = FieldEncryptor(StaticKeyProvider({"KEY-V1": old_key, "KEY-V2": new_key}, "KEY-V2"))

    first = old.encrypt("+91XXXXXXXXXX", field_name="subject_contacts.contact_value")
    second = old.encrypt("+91XXXXXXXXXX", field_name="subject_contacts.contact_value")
    assert first != second
    assert "+91XXXXXXXXXX" not in first
    assert old.decrypt(first, field_name="subject_contacts.contact_value") == "+91XXXXXXXXXX"
    assert rotated.reencrypt(first, field_name="subject_contacts.contact_value") != first
    assert (
        rotated.decrypt(
            rotated.reencrypt(first, field_name="subject_contacts.contact_value"),
            field_name="subject_contacts.contact_value",
        )
        == "+91XXXXXXXXXX"
    )

    envelope = json.loads(first)
    envelope["ciphertext"] = envelope["ciphertext"][:-2] + "AA"
    with pytest.raises(EncryptionError):
        old.decrypt(json.dumps(envelope), field_name="subject_contacts.contact_value")
    with pytest.raises(EncryptionError):
        FieldEncryptor(StaticKeyProvider({"OTHER": b"3" * 32}, "OTHER")).decrypt(
            first, field_name="subject_contacts.contact_value"
        )


@pytest.mark.asyncio
async def test_oidc_verifier_rejects_invalid_tokens_and_accepts_rotation() -> None:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
    public_jwk.update({"kid": "KEY-V1", "alg": "RS256", "use": "sig"})
    provider = OIDCIdentityProvider(
        issuer="https://issuer.example.test",
        audience="sambal-api",
        jwks_uri="https://issuer.example.test/.well-known/jwks.json",
        provider_code="TEST_IDP",
        algorithms=["RS256"],
        jwks_loader=lambda: _jwks(public_jwk),
    )
    now = datetime.now(UTC)
    payload = {
        "iss": "https://issuer.example.test",
        "aud": "sambal-api",
        "sub": "external-operator-1",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    token = jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "KEY-V1"})
    validated = await provider.validate_token(token)
    assert validated.subject == "external-operator-1"
    assert validated.provider_code == "TEST_IDP"

    expired = jwt.encode(
        {**payload, "exp": now - timedelta(minutes=1)},
        private_key,
        algorithm="RS256",
        headers={"kid": "KEY-V1"},
    )
    wrong_audience = jwt.encode(
        {**payload, "aud": "other-api"}, private_key, algorithm="RS256", headers={"kid": "KEY-V1"}
    )
    wrong_issuer = jwt.encode(
        {**payload, "iss": "https://other-issuer.example.test"},
        private_key,
        algorithm="RS256",
        headers={"kid": "KEY-V1"},
    )
    malformed = "not.a.jwt"
    unsigned = jwt.encode(payload, key=None, algorithm="none", headers={"kid": "KEY-V1"})
    for invalid in (expired, wrong_audience, wrong_issuer, malformed, unsigned):
        with pytest.raises(TokenValidationError):
            await provider.validate_token(invalid)

    unknown_key = jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "UNKNOWN"})
    with pytest.raises(TokenValidationError):
        await provider.validate_token(unknown_key)


async def _jwks(key: dict[str, object]) -> dict[str, object]:
    return {"keys": [key]}
