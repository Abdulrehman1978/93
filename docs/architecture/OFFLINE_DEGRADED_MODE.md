# Offline & Degraded Mode Resilience Architecture

> **Document ID:** ARCH-OFFLINE-DEGRADED-V2  
> **Topic:** High-Availability Degradation Architecture & Failure Boundary Design  
> **Core Mandate:** A cloud outage must NEVER prevent a victim in crisis from logging a complaint or receiving immediate safety protection.

---

## 1. System Failure Matrix & Degraded Behaviors

| Component / Failure Mode | Root Cause Trigger | Primary Impact | Degraded Mode Fallback State | Operational Capability Retained |
| :--- | :--- | :--- | :--- | :--- |
| **External LLM Cloud API Outage** | Network timeout, API quota exhaustion, upstream cloud failure. | Semantic narrative summaries and rich counterfactual suggestions cannot be generated. | **`DEGRADED_DETERMINISTIC_MODE`** | **100% of core intake functions.** Local ASR operates; Layer 1 deterministic regex safety rules fire in < 1ms; SVI calculated via baseline heuristic weights; referrals queue locally. |
| **External Cloud Translation Failure** | Translation service downtime. | Vernacular transcripts cannot be translated into English for central dashboard review. | **`ORIGINAL_SCRIPT_PRESERVATION`** | Narrative preserved in original Indic script (Devanagari, Bengali, Tamil, etc.); operator prompted to handle in native language; zero token dropping. |
| **High Audio Noise / Static (SNR < 10dB)** | Bad cellular connection, speakerphone echo. | Acoustic feature extraction (F0, tremor) becomes mathematically unreliable. | **`ACOUSTIC_ABSTENTION_MODE`** | Affective Signal Engine emits `LOW_AUDIO_QUALITY_ABSTAIN`; acoustic weight clamped to 0; SVI computed purely on textual statements and structural context; operator prompted to request caller repeat. |
| **External Referral Webhook Failure** | Target agency server down (e.g. Tele-MANAS server timeout). | Outgoing referral payload cannot be immediately acknowledged. | **`LOCAL_SPOOL_AND_RETRY`** | Referral stored in PostgreSQL with status `DISPATCH_PENDING`; exponential backoff worker retries; SMS confirmation queued; supervisor alerted if retry window exceeds 2 hours. |
| **Complete Internet Disconnection (Local Center)** | WAN fiber cut at district call center. | Center isolated from central ministry cloud. | **`LOCAL_ISOLATED_NODE_MODE`** | Local server runs SQLite/PostgreSQL, local `faster-whisper`, and local Next.js frontend; calls continue on local PRI lines; dockets spooled locally for batch sync when fiber restores. |

---

## 2. Degraded Mode State Machine & Circuit Breakers

The system implements an automated **Circuit Breaker** on all external model and API calls:

```python
class DegradationManager:
    """Monitors service health and dynamically toggles degraded mode."""
    
    def __init__(self):
        self.state: Literal["NORMAL", "DEGRADED", "EMERGENCY_MINIMAL"] = "NORMAL"
        self.consecutive_failures: int = 0
        self.failure_threshold: int = 3
        
    def record_llm_failure(self):
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.state = "DEGRADED"
            logger.warning("CIRCUIT BREAKER OPEN: Switching to DEGRADED_DETERMINISTIC_MODE")
            
    def record_llm_success(self):
        self.consecutive_failures = 0
        if self.state != "NORMAL":
            self.state = "NORMAL"
            logger.info("CIRCUIT BREAKER CLOSED: Restoring full contextual AI capabilities")
```

### Visual Indicator on Operator Live Copilot:
When operating in degraded mode, the system prominently displays an amber status banner:
> ⚠️ **SYSTEM OPERATING IN DEGRADED RESILIENCE MODE**  
> *External contextual AI temporarily offline. Deterministic safety rules and local speech recognition active. All emergency triage rules functional.*
