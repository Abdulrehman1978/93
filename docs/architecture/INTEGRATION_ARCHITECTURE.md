# Government & External Integration Architecture

> **Document ID:** ARCH-INTEGRATION-GATEWAY-V2  
> **Topic:** External Agency Integration, Adapter Abstractions, and Webhook Reliability  
> **Standard:** Complete OpenAPI 3.1 compliance, Cryptographic Webhook Security, and Zero Fabricated APIs.

---

## 1. Headless Integration Architecture

```text
               SAMBAL MODULAR INTELLIGENCE MONOLITH
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     │                           │                           │
     ▼                           ▼                           ▼
[ CHANNEL ADAPTERS ]    [ INTELLIGENCE APIS ]    [ SUPPORT SERVICE ADAPTERS ]
• Web PWA Gateway       • `/api/v1/sessions`     • `TeleManasAdapter`
• IVR Telephony Gateway • `/api/v1/assessments`  • `LegalAidAdapter`
• SAMBAL Portal Widget  • `/api/v1/safety`       • `ERSS112Adapter`
• Future Chatbot Engine • `/api/v1/referrals`    • `SAMBALCaseAdapter`
```

---

## 2. Canonical Agency Adapters & Contract Interfaces

```python
class BaseSupportAdapter(ABC):
    """Canonical interface for external public sector and emergency adapters."""
    
    @abstractmethod
    async def dispatch_referral(
        self, payload: SafeHandoffPayload, idempotency_key: str
    ) -> AdapterDispatchResult:
        """Dispatches a consented referral payload to external agency endpoint."""
        pass

    @abstractmethod
    async def verify_webhook_signature(
        self, signature: str, raw_body: bytes, timestamp: int
    ) -> bool:
        """Cryptographically verifies incoming webhook authenticity via HMAC SHA-256."""
        pass

    @abstractmethod
    async def check_service_health(self) -> AdapterHealthStatus:
        """Returns health status: LIVE, SANDBOX, or ADAPTER_READY with latency telemetry."""
        pass
```

### 1. `TeleManasAdapter` (MoHFW Tele-Mental Health)
- **Status:** `SANDBOX` (Production interface ready; awaiting MoHFW token).
- **Endpoint:** `POST /api/v1/integrations/telemanas/handoff`
- **Features:** Dispatches trauma summary; listens for callbacks on `POST /api/v1/webhooks/telemanas/status`.
- **Payload Security:** Payload encrypted with AES-256-GCM; signed with agency secret.

### 2. `LegalAidAdapter` (NALSA / DLSA Free Legal Aid)
- **Status:** `SANDBOX`.
- **Endpoint:** `POST /api/v1/integrations/nalsa/docket-referral`
- **Features:** Packages statutory victim rights notification under Section 15A of PoA Act; transmits to DLSA front-office portal.

### 3. `ERSS112Adapter` (Emergency Response Support System / Police Protection)
- **Status:** `SANDBOX`.
- **Endpoint:** `POST /api/v1/integrations/erss112/dispatch`
- **Mandatory Human-Authorized Handoff Boundary:** An AI score, threshold breach, or safety model event may recommend escalation, but **may NOT autonomously contact law enforcement or emergency services** unless a future formally approved government statutory policy explicitly authorizes such behavior.
- **Workflow:** The system surfaces a high-priority alert on the Operator Live Copilot. Transmission to `ERSS112Adapter` strictly requires the 14566 helpline operator to verbally verify immediate danger and explicitly click `[AUTHORIZE EMERGENCY ESCALATION]`.
- **Telemetry:** In sandbox mode, triggers simulated dispatch confirmation with simulated vehicle dispatch telemetry and auditable operator sign-off.

### 4. `SAMBALCaseAdapter` (MoSJE Core Docket Synchronization)
- **Status:** `ADAPTER_READY`.
- **Function:** Synchronizes external Docket IDs, FIR registration numbers, and District Magistrate review statuses into the SAMBAL intelligence layer.

---

## 3. Webhook Quality & Enterprise Reliability

To ensure robust communication over public and government wide-area networks:
1. **HMAC SHA-256 Signatures:** Every outgoing and incoming webhook includes an `X-Signature-SHA256` header calculated over `timestamp + "." + raw_payload`.
2. **Replay Protection Window:** Requests with a timestamp skew greater than 300 seconds (5 minutes) are rejected with HTTP 401.
3. **Idempotency Enforcement:** All dispatch requests require a unique UUID `X-Idempotency-Key`. Duplicate keys within a 24-hour window return the cached initial response, preventing duplicate referrals.
4. **Exponential Backoff & Dead-Letter Queue (DLQ):** Failed webhook dispatches retry at intervals: 15s, 1m, 5m, 15m, 1h. If all retries fail, the transaction enters a database-backed Dead-Letter Queue and triggers a supervisor alert.
