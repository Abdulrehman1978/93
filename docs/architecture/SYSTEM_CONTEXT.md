# System Context & C4 Architectural Boundaries

> **Document ID:** ARCH-SYSTEM-CONTEXT-V2  
> **Standard:** C4 Model — Level 1: System Context  
> **Topic:** SAMBAL Multilingual Trauma-Aware Intelligence & Response Layer

---

## 1. System Context Diagram (C4 Level 1)

```text
                                  ┌────────────────────────┐
                                  │ Complainant / Citizen  │
                                  │ (SC/ST Atrocity Victim)│
                                  └───────────┬────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    │ (Voice Call 14566)      │ (Web Portal Text)       │ (Silent PWA Intake)
                    ▼                         ▼                         ▼
        ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐
        │ Existing NHAA / PSTN  │ │ Existing SAMBAL Web   │ │ SAMBAL Citizen Web    │
        │ Telephony Trunk (14566)│ │ Portal (Grievance Form)│ │ & Silent PWA App      │
        └───────────┬───────────┘ └───────────┬───────────┘ └───────────┬───────────┘
                    │                         │                         │
                    └─────────────────────────┼─────────────────────────┘
                                              │
                                              ▼
                    =====================================================
                    SAMBAL INTELLIGENCE & RESPONSE LAYER (THE SYSTEM)
                    "Understand Sooner. Respond Safer. Stay Until Support Arrives."
                    =====================================================
                                              │
        ┌───────────────────┬─────────────────┼─────────────────┬───────────────────┐
        │ (Live Assistance) │ (Case Review)   │ (Consented      │ (Dispatched       │ (Docket Sync)
        ▼                   ▼                 ▼  Safe Handoff)  ▼  Safety Alert)    ▼
┌──────────────┐    ┌──────────────┐   ┌──────────────┐  ┌──────────────┐   ┌──────────────┐
│ 14566 Live   │    │ Case Quality │   │ Tele-MANAS   │  │ Police / ERSS│   │ MoSJE SAMBAL │
│ Helpline     │    │ Supervisor / │   │ (14416) &    │  │ (112) / Atro-│   │ Core CRM &   │
│ Operator     │    │ District Off.│   │ DLSA Legal   │  │ city Cell DSP│   │ Docket Store │
└──────────────┘    └──────────────┘   └──────────────┘  └──────────────┘   └──────────────┘
```

---

## 2. Actors & Primary Interactions

### 1. Complainant / Citizen
- **Profile:** An individual from a Scheduled Caste or Scheduled Tribe community who has experienced discrimination, assault, boycott, or intimidation.
- **Interactions:**
  - Initiates contact via Voice (dialing 14566), Web form, or Silent tap-flow.
  - Grants explicit, granular consent for voice transcription and referral sharing.
  - Receives live empathetic engagement without exposure to clinical scores.
  - Tracks referral progress through a non-stigmatizing case portal.

### 2. Helpline Operator (NHAA Staff)
- **Profile:** Trained government call handler operating the 14566 live queue.
- **Interactions:**
  - Observes real-time streaming transcript with synchronized risk markers.
  - Views the three-dimensional triage panel (Immediate Safety, SVI, Urgency).
  - Uses AI-suggested trauma-informed follow-up questions.
  - Overrides or confirms AI support recommendations; dispatches referrals.

### 3. Case Supervisor & District Welfare Officer
- **Profile:** Senior administrator overseeing helpline operations and SLA adherence.
- **Interactions:**
  - Monitors high-priority and escalated case queues.
  - Resolves blocked referrals (e.g. legal aid unacknowledged after 48h).
  - Inspects district-level resource gaps to reallocate local mental health personnel.

### 4. Support Providers (Tele-MANAS & NALSA/DLSA)
- **Profile:** External psychological counselors (14416) or appointed legal aid lawyers.
- **Interactions:**
  - Receives redacted, consented "Safe Handoff" summaries via secure adapter.
  - Acknowledges referrals and schedules victim appointments without forcing re-traumatizing narrative retelling.
  - Reports service initiation back to SAMBAL to close the loop.
