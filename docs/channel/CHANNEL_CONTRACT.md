# Packet 06 — Channel API Contract

## Public routes

| Method | Route | Auth boundary | Purpose |
| --- | --- | --- | --- |
| `GET` | `/api/v1/channel/capabilities` | Public | Declares capability truth |
| `POST` | `/api/v1/channel/sessions` | Public | Creates a `WEB` session |
| `GET` | `/api/v1/channel/sessions/{session_id}` | Session token | Reads state without exposing credentials |
| `GET` | `/api/v1/channel/sessions/{session_id}/policy` | Session token | Presents notices and policy |
| `POST` | `/api/v1/channel/sessions/{session_id}/consents` | Session token | Records one purpose decision |
| `POST` | `/api/v1/channel/sessions/{session_id}/mode` | Session token | Selects a supported mode |
| `POST` | `/api/v1/channel/sessions/{session_id}/complete` | Session token | Closes a completed interaction |
| `POST` | `/api/v1/channel/sessions/{session_id}/abandon` | Session token | Closes an abandoned interaction |

The session token is sent as `X-Channel-Session-Token`. Invalid, expired, idle, completed, and unknown sessions receive the same safe authorization detail; raw tokens never appear in logs, audit metadata, or database fields.

Consent requests require `purpose_code`, `choice`, the current `policy_version`, and a client-generated `client_action_id`. The server derives subject, channel, actor provenance, lawful basis, policy row, and processing scope.

The shared Zod contracts in `packages/contracts/src/index.ts` mirror these schemas. RFC 7807 errors use typed status, request correlation, and stable error URIs.
