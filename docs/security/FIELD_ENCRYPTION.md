# Packet 04 Field Encryption

Highly sensitive text fields use application-level AES-256-GCM envelopes through `backend/app/security/encryption.py`.

```json
{
  "version": 1,
  "algorithm": "AES-256-GCM",
  "key_id": "KEY-VERSION",
  "nonce": "base64url-12-byte-nonce",
  "ciphertext": "base64url-ciphertext-and-tag"
}
```

The logical field name is authenticated as AES-GCM associated data, so moving an envelope to another field fails authentication. Each encryption uses a fresh nonce. Decryption rejects malformed envelopes, unavailable key versions, wrong keys, tampering, and field mismatches without returning plaintext or key material in the error.

`KeyProvider` is the boundary for KMS/HSM/Vault or a mounted deployment secret. Keys are never stored in PostgreSQL or source. Versioned key configuration permits rotation and `reencrypt` migration. Production configuration fails fast unless key material is present.

`EncryptedText` is the normal ORM storage boundary for `subject_contacts.contact_value`, `transcript_segments.content`, and `translations.translated_content`. It encrypts plaintext on every ORM bind and has no plaintext fallback. Result decryption fails closed unless a policy-enforced sensitive access service has opened the exact field scope after authorization. DTO projections remain mandatory even when a field is encrypted.

Verification writes all three fields through the ORM, inspects raw PostgreSQL values for plaintext absence, then reads through the authorized application boundary. It also covers nonce uniqueness, old-key reads after rotation, wrong-key, tamper, unauthorized ORM reads, and field-bound AAD failures.
