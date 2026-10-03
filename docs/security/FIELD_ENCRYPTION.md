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

The first protected field is `subject_contacts.contact_value`; the same codec is available to transcript, translation, narrative, and other highly sensitive field owners when those features are implemented. DTO projections remain mandatory even when a field is encrypted.

Verification includes nonce uniqueness, raw SQL plaintext absence, round trip, rotation, wrong-key, tamper, and wrong-field failures.
