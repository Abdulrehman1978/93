# Packet 06 — Anonymous Session Security Policy

Policy version: `packet-06-internal-v1`.

Sessions use 32 bytes of cryptographically secure random material encoded with `token_urlsafe`. Only the lowercase SHA-256 digest is stored in `interactions.session_token_digest`; the raw token is returned once and is never recoverable from the database.

Default limits are a 30-minute inactivity/TTL window with a 15-minute idle timeout and a one-hour absolute maximum. A mutating request refreshes `last_activity_at` only while the absolute maximum remains valid. Session state is closed by explicit completion or abandonment.

Metadata is database-validated through `validate_channel_metadata`. Only provider code/reference, protocol version, capability flags, external reference, and client request ID are permitted. Raw payloads, browser fingerprints, IP addresses, audio, and narrative text are not accepted by the channel interaction record.

Client request IDs are unique per channel and are conflict-safe. Consent action IDs are unique per interaction and purpose ledger; reuse with different content produces a conflict. This is idempotency, not a claim of exactly-once delivery across an unavailable client network.
