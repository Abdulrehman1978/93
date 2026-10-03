# SAMBAL Intelligence & Response Layer — Master Product Specification V2

> **Document ID:** MASTER-PRODUCT-SPEC-V2  
> **Status:** APPROVED & BINDING — Supersedes V1 in Full  
> **Problem Statement:** SIH26093 — AI-Based Real-Time Stress and Trauma Assessment Module for Victims/Complainants Accessing NHAA (14566) and Integrated Portal  
> **Sponsoring Body:** Ministry of Social Justice and Empowerment (MoSJE), Department of Social Justice and Empowerment (DoSJE)  
> **Working Product Concept:** SAMBAL Intelligence & Response Layer  
> **Working Tagline:** *Understand sooner. Respond safer. Stay until support arrives.*  
> **Product Philosophy:** *From first signal to verified support.*  
> **Infrastructure Philosophy:** *Maximum useful capability, minimum operational complexity.*

---

## 1. Primary Product Definition & Full Value Chain

The **SAMBAL Intelligence & Response Layer** is:
> A multilingual AI-assisted intelligence and response layer for SAMBAL / NHAA that analyses voice and text during first contact, identifies safety and vulnerability signals in real time, produces an explainable Stress Vulnerability Index, assists trained officials with appropriate next actions, orchestrates authorized support referrals, and tracks whether meaningful support actually reaches the complainant.

### The Complete Value Chain:
```text
FIRST CONTACT (14566 Voice / Portal Text / Silent PWA)
      ↓
UNDERSTAND (Multilingual ASR, Indic NLP, DSP Acoustics)
      ↓
ASSESS (Immediate Safety Gate + SVI 0-100 + Incident Urgency)
      ↓
EXPLAIN (Evidence Inspector, Exact Snippet & Attribution)
      ↓
HUMAN REVIEW (14566 Operator Co-Pilot & Oversight)
      ↓
RESPOND (Protocol-backed Suggested Trauma Questions)
      ↓
REFER (Consented Safe Handoff to Tele-MANAS, DLSA, ERSS)
      ↓
TRACK (Closed-Loop Referral State Machine & SLA Timers)
      ↓
FOLLOW UP (Policy-Driven `FollowUpPolicy` Cadence)
      ↓
MEASURE OUTCOME (District Resource Gaps & Welfare Intelligence)
```

---

## 2. The Three Non-Negotiable Core Differentiators (USPs)

### USP 1 — Three-Dimensional Risk Understanding
Rather than collapsing complex trauma and legal danger into a single arbitrary score, the system maintains three orthogonal dimensions:
1. **Immediate Safety Gate:** Evaluates imminent physical peril, active violence, or explicit self-harm intent. Triggers fast-path emergency workflows.
2. **Stress Vulnerability Index (SVI: 0–100):** Evaluates psychological, emotional, and structural vulnerability across Low, Moderate, High, and Critical bands. Operates under `SVI_POLICY_STATUS = PROVISIONAL_TRIAGE_POLICY` pending Packet 11 calibration.
3. **Reported Incident Urgency:** Identifies facts potentially relevant to urgency, statutory protection categories, and time-sensitive legal deadlines regardless of caller emotional expression. The system does NOT determine whether a crime legally occurred, whether an offence is proven, or whether a person is guilty. Legal characterization remains an authorized human/government responsibility.
- **The Golden Rule Solved:** A complainant speaking in a calm, flat, dissociated monotone about an ongoing violent assault is correctly assigned **CRITICAL URGENCY** and **CRITICAL SAFETY**, completely overriding the low acoustic arousal.

### USP 2 — Evidence Instead of Mysterious AI
No operator, supervisor, or judge is ever forced to accept an opaque "Trauma Score = 87". Every output is fully explainable in the **Evidence Inspector**:
- What exact text or acoustic snippet triggered the flag?
- What was the start and end timestamp in the interaction?
- Which model and policy version generated it?
- What was the model's confidence and the underlying audio quality (SNR)?
- Exactly how many points did this item contribute to the SVI?
- Counterfactual control: *"What would the SVI be if acoustic features were excluded?"*

### USP 3 — Detection to Verified Support (The Closed Loop)
The system does not terminate at a passive recommendation card. It orchestrates and verifies the complete referral journey:
$$\text{Recommended} \longrightarrow \text{Approved} \longrightarrow \text{Dispatched} \longrightarrow \text{Acknowledged} \longrightarrow \text{Contacted} \longrightarrow \text{Service Started} \longrightarrow \text{Follow-Up} \longrightarrow \text{Verified Outcome}$$
The platform answers the fundamental question of public service: **"Did the victim actually receive help?"**

---

## 3. Non-Negotiable Ethical & Diagnostic Boundaries

1. **Decision Support, NOT Diagnosis:** The system provides trauma-informed, safety-informed triage assistance; it does NOT output psychiatric or medical diagnoses (no "PTSD detected" or "Severe Depression diagnosed"). All thresholds represent a *provisional triage policy* requiring domain/clinical validation before production certification.
2. **Strict Ban on Truth / Lie Detection:** The system never evaluates "credibility", "truth probability", or "fake victim scores". Voice stress analysis is scientifically discredited for truth detection.
3. **Zero Demographic Profiling:** The system never infers caste, religion, sexual orientation, or character from voice acoustics.
4. **Mandatory Human-Authorized Handoff Boundary:** An AI score or model event may recommend escalation but **may NOT autonomously contact law enforcement or emergency services** (`ERSS112Adapter`) unless a future formally approved policy explicitly authorizes such behavior. High-impact interventions strictly require human operator authorization.
5. **No Autonomous Crime / Guilt Determination:** The system identifies facts potentially relevant to urgency or statutory routing. It does NOT determine that a crime legally occurred or that a person is guilty.
6. **Ephemeral Raw Audio:** Raw voice streams are discarded after feature extraction unless explicit complainant consent is granted for evidence archiving.

---

## 4. User Personas & Experience Surfaces

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                CITIZEN EXPERIENCE                                      │
│  • Routes: `/`, `/intake/voice`, `/intake/text`, `/intake/silent`, `/my-case/[id]`     │
│  • Three unencumbered choices: SPEAK (Voice), WRITE (Text), or SILENT (Discreet Tap)   │
│  • Quick Exit button, plain-language consent, zero confusing diagnostic jargon         │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                OPERATOR LIVE COPILOT                                   │
│  • Routes: `/operator/queue`, `/operator/live/[sessionId]`, `/operator/cases/[id]`     │
│  • High-density, real-time synchronized Waveform, Live Transcript, and Evidence Pins   │
│  • 3D Triage Panel, Suggested Trauma Questions, Referral Dispatcher, Feedback Loop     │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                COUNSELLOR PORTAL                                       │
│  • Routes: `/support/referrals`, `/support/referrals/[id]`, `/support/followups`       │
│  • Redacted "Safe Handoff" summaries; zero irrelevant legal allegations exposed        │
│  • Appointment scheduler, session status updater, closed-loop callback generator       │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          SUPERVISOR & MINISTRY INTELLIGENCE                            │
│  • Routes: `/supervisor/queue`, `/admin/outcomes`, `/admin/resource-gaps`              │
│  • Escalation queues for SLA breaches; privacy-preserving district resource gap maps   │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                            │
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                JUDGE LAB & EVIDENCE CENTER                             │
│  • Routes: `/demo/lab`, `/demo/evidence`, `/demo/traceability`, `/demo/failure-modes`  │
│  • Interactive pipeline execution on Golden Scenarios A-H; model cards; truth states   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Technology Stack Summary (V3 Lean-Core Architecture)

```text
Next.js PWA
      ↓
FastAPI Modular Monolith
      ↓
PostgreSQL 16+ (Canonical)
      ↓
S3-Compatible Object Storage
      ↓
PostgreSQL-Backed Async Job Queue
      ↓
External / Government Provider Adapters
```

- **Frontend Surfaces:** Next.js 14/15 (App Router), React, Tailwind CSS (Civic Calm Design System), Web Audio API, Canvas Waveform.
- **Backend Core:** FastAPI Modular Monolith (Python 3.12+), Uvicorn, Pydantic v2, SQLAlchemy v2.
- **Speech & DSP:** `faster-whisper-turbo` (CTranslate2 INT8 quantized) as **`BASELINE_CANDIDATE`** for local execution; final selection subject to Packet 08 benchmarking against Indic alternatives. Native DSP via `librosa` (pyin F0, RMS, spectral flux) and `webrtcvad`.
- **Database:** **PostgreSQL 16+ is canonical** across dev, testing, E2E, CI, staging, and production. Table budget is approximately **32–40 core relational tables** ($\le 45$ upper budget limit). SQLite is restricted solely to deliberately DB-agnostic unit tests.
- **Security & Privacy:** DPDP-ready consent engine, AES-256 field encryption, purpose-scoped RBAC, SHA-256 webhook signatures.
- **Packaging:** Multi-stage Docker & Docker Compose; zero-dependency offline local bootstrap.
