# Capability Truth State Register

> **Document ID:** CAPABILITY-STATUS-REGISTER-V2  
> **Standard:** Absolute transparency on runtime status. Zero fabricated integrations, zero fake "live" badges.  
> **Allowed States:** `LIVE` | `SANDBOX` | `ADAPTER_READY` | `RESEARCH_ONLY`

---

## 1. Capability Status Matrix

| Capability / Module | Runtime Truth State | Operational Description & Execution Boundary | Evidence Artifact / Provider |
| :--- | :--- | :--- | :--- |
| **Local Indic ASR (Speech-to-Text)** | `BASELINE_CANDIDATE` | Initial local implementation candidate using CTranslate2 INT8 `faster-whisper-turbo`. Final selection subject to Packet 08 benchmarking against Indic-focused/government alternatives. | `faster-whisper` local model weights; benchmark suite in Packet 08. |
| **DSP Acoustic Feature Extraction** | `LIVE` | Mathematical DSP extraction of F0 (pyin), energy (RMS), pause statistics, and speech rate using librosa and WebRTC VAD. | `app/intelligence/speech.py`; unit tests in `tests/test_speech_analytics.py`. |
| **Deterministic Safety Gate** | `LIVE` | Multilingual regex and statutory lexicon rule engine detecting imminent self-harm, active violence, weapons, and coercion. | `app/safety/rules.py`; unit tests in `tests/test_safety_gate.py`. |
| **Semantic NLP Threat Classifier** | `LIVE` | Multilingual transformer-based semantic classification for threat extraction, negation disambiguation, and reported speech. | `app/intelligence/text.py`; unit tests in `tests/test_text_safety.py`. |
| **Multimodal Evidence Fusion & SVI** | `LIVE` | Mathematically bounded weighted fusion engine calculating SVI (0–100, `PROVISIONAL_TRIAGE_POLICY`), risk bands, and counterfactual contributions. | `app/intelligence/svi.py`; unit tests in `tests/test_svi_fusion.py`. |
| **Canonical PostgreSQL Database** | `LIVE` | Authoritative relational database for all environments (dev, test, CI, prod). Schema designed within 32–40 core tables budget (upper limit $\le 45$). | PostgreSQL 16+ instance; Alembic migrations in `alembic/`. |
| **Closed-Loop Referral State Machine** | `LIVE` | Full relational state machine tracking referral lifecycle (Recommended → Acknowledged → Contacted → Service Started → Follow-up). | `app/referral/lifecycle.py`; unit tests in `tests/test_referrals.py`. |
| **Citizen Intake (Speak / Write / Silent)** | `LIVE` | Responsive PWA interface providing 3 distinct intake modalities, audio recording, real-time draft saving, and Quick Exit. | Next.js frontend routes `/intake/*`; E2E tests in `tests/e2e/intake.spec.ts`. |
| **Operator Live Response Copilot** | `LIVE` | Real-time WebSocket-synchronized dashboard displaying live transcript, evidence pins, SVI dial, and suggested questions. | `/operator/live/[sessionId]`; Playwright tests in `tests/e2e/copilot.spec.ts`. |
| **Evidence Timeline & Inspector** | `LIVE` | Synchronized audio waveform, transcript timeline, and drill-down Evidence Inspector revealing exact provenance and confidence. | `/operator/live` inspector drawer; tests in `tests/e2e/evidence.spec.ts`. |
| **Tele-MANAS Handoff Adapter** | `SANDBOX` | Production-grade simulation of the MoHFW Tele-MANAS (14416) referral intake webhook. Validates HMAC signatures and returns simulated case IDs. | `app/integrations/telemanas.py`; sandbox tests in `tests/test_telemanas_sandbox.py`. |
| **NALSA / DLSA Legal Aid Adapter** | `SANDBOX` | Production-grade simulation of District Legal Services Authority front-office referral docket transmission with bi-directional callback. | `app/integrations/nalsa.py`; sandbox tests in `tests/test_nalsa_sandbox.py`. |
| **ERSS 112 Emergency Dispatch** | `SANDBOX` | High-priority emergency payload simulator with mandatory human operator authorization gate. Autonomous dispatch strictly prohibited. | `app/integrations/erss112.py`; sandbox tests in `tests/test_erss_sandbox.py`. |
| **SAMBAL / NHAA Docket Sync Adapter** | `ADAPTER_READY` | Canonical API client implementing MoSJE grievance docket synchronization contracts. Complete OpenAPI specification awaiting production VPN credentials. | `app/integrations/sambal_adapter.py`; contract tests in `tests/test_sambal_adapter.py`. |
| **BHASHINI MeitY Cloud ASR** | `ADAPTER_READY` | Enterprise adapter configured for Digital India Bhashini Division API v2. Awaiting production API tokens; fallback to local candidate. | `app/speech/bhashini_adapter.py`; mock contract tests in `tests/test_bhashini_adapter.py`. |
| **Affective Distress Classifier** | `RESEARCH_ONLY` | Experimental prosodic emotion classification model fine-tuned on public speech datasets. Bounded to supporting signal role (max ±15 pts SVI). | `app/intelligence/affective.py`; documented in `docs/ai/AFFECTIVE_SIGNAL_ENGINE.md`. |
| **Offline Degraded Mode Fallback** | `LIVE` | System resilience manager automatically dropping external LLM dependencies during network outages while maintaining intake and safety rules. | `app/core/resilience.py`; failure injection tests in `tests/test_degraded_mode.py`. |

---

## 2. Transition Gate Requirements
- **To move from `SANDBOX` to `LIVE`:** Requires verified production credentials, signed inter-ministerial data sharing agreement, and end-to-end integration test against staging environment.
- **To move from `ADAPTER_READY` to `LIVE`:** Requires NIC/MoSJE API endpoint access, mTLS certificate exchange, and security compliance audit.
- **To move from `RESEARCH_ONLY` to `LIVE`:** Requires formal clinical validation study with institutional review board (IRB) ethics approval and domain publication.
