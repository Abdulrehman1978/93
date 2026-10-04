# Packet 07 — Citizen Intake (Speak / Write / Silent)

Status: Implementation complete; owner review pending.

## Promise and boundary

Citizen intake is a trauma-informed, privacy-minimizing first-party web flow. A person may choose Write, Speak, or Silent intake, may stop at any point, and is never required to supply a name, legal characterization, exact location, or contact detail. The service does not diagnose, score credibility, dispatch emergency services, deliver messages, or promise a response time.

Speak is deliberately truthful but pre-capture in Packet 07: the browser does not call `getUserMedia`, `MediaRecorder`, Web Speech, an ASR provider, or an audio upload endpoint. The page clearly offers Write and Silent alternatives.

## Flow contract

1. The public home page creates no session. The user intentionally starts at `/help`.
2. The server creates an anonymous short-lived session and the UI renders the actual server policy/notice response.
3. The user continues through `/intake/continue`; the server derives the PURP-01 authorization.
4. The user selects exactly one mode. Write and Silent use the channel session token in a header; tokens and content never appear in URLs, analytics, or generic metadata.
5. Write collects a required narrative and optional when, location, safety, contact preference, and contact value. The narrative is reviewed before submission and is not normalized or sent to NLP.
6. Silent asks one question at a time: current safety, urgent help, and contact preference, followed by an optional contact value.
7. Submission atomically creates one OPEN NORMAL case, stores encrypted entries, binds the interaction, promotes active authorizations, records safe event/audit metadata, completes the interaction, and returns an opaque reference.

## Choices and safety semantics

Current safety: `YES`, `NO_SOMEONE_MAY_BE_NEARBY`, `NOT_SURE`, `SKIP`.

Urgent help: `YES_AS_SOON_AS_POSSIBLE`, `NO`, `NOT_SURE`, `SKIP`.

Contact preference: `DO_NOT_CALL`, `SILENT_SMS_PREFERRED`, `WHATSAPP_PREFERRED`, `ASK_ME_LATER`, `NO_CONTACT_DETAILS_NOW`. Any collected contact value is encrypted and starts with `safe_to_use = false`; no delivery or dispatch is performed.

## Recovery and idempotency

Draft text is kept only in namespaced `sessionStorage` so a network failure can be retried without losing work. An opaque `client_submission_id` is reused for the retry. The API returns the same receipt for a completed same-session retry and rejects a different submission, an expired/closed/cross-session token, a wrong mode, or a missing PURP-01 authorization.

## Accessibility and language

The flow uses semantic headings, labelled controls, visible focus, keyboard-safe buttons, one-question-at-a-time Silent interaction, responsive layouts at 320/390/1440 widths, and a language control limited to the truthful foundation language set. No third-party analytics or hidden audio capability is present.
