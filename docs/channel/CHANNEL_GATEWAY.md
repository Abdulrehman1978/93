# Packet 06 — Canonical Channel Gateway

Status: implementation baseline; external provider adapters are not live.

The gateway is the only supported entry boundary for an interaction. It normalizes channel provenance before domain services see an event and exposes a narrow, versioned API under `/api/v1/channel`.

## Capability truth

| Channel | Status | Public in Packet 06 | Modes | Provider |
| --- | --- | --- | --- | --- |
| `WEB` | `LIVE_TESTED` | Yes | `UNSELECTED`, `TEXT` | None; first-party gateway |
| `PORTAL` | `ADAPTER_READY` | No | All canonical modes | Not configured |
| `IVR` | `NOT_CONFIGURED` | No | `VOICE` | Not configured |
| `TELEPHONY` | `NOT_CONFIGURED` | No | `VOICE` | Not configured |
| `CHATBOT` | `NOT_CONFIGURED` | No | `TEXT` | Not configured |
| `MOBILE` | `NOT_CONFIGURED` | No | All canonical modes | Not configured |
| `OPERATOR` | `ADAPTER_READY` | No | All canonical modes | Authenticated human boundary required |
| `SYSTEM` | `ADAPTER_READY` | No | All canonical modes | Internal provenance only |

`ADAPTER_READY` and `NOT_CONFIGURED` are explicit capability states, not claims of integration. Packet 06 imports no telephony, IVR, chatbot, or government-provider SDK.

## Interaction lifecycle

1. `POST /api/v1/channel/sessions` creates a pseudonymized subject and an open interaction.
2. The raw token is returned once. PostgreSQL stores only its SHA-256 digest.
3. `GET /sessions/{id}/policy` presents the versioned notice/consent policy and records a safe `NOTICE_PRESENTED` event.
4. Consent, mode selection, completion, and abandonment use explicit typed endpoints.
5. Case binding is an internal service operation; it validates subject equality and promotes active interaction authorizations without rewriting history.

No anonymous endpoint accepts free-form narrative, audio, arbitrary metadata, actor identity, lawful basis, or processing scope fields.
