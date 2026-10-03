# Demo & Golden Scenario Coverage Matrix

> **Document ID:** DEMO-COVERAGE-MATRIX-V2  
> **Topic:** Comprehensive Traceability for SIH Judge Demonstrations and Test Scenarios  
> **Date:** October 2026

---

## 1. Three-Minute Golden Demo Walkthrough

| Timestamp Range | Demo Segment | Key Action / Flow | UI Surface | Backend Trigger | Verified Differentiation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0:00 – 0:20** | **The Core Problem** | Highlight that 14566 operators lack real-time trauma triage tools; introduce SAMBAL Intelligence Layer. | Landing Hero (`/`) | Public Trust Service Status | Replaces generic grievance portals with an augmented intelligence layer. |
| **0:20 – 0:45** | **Citizen First Contact** | Select `SPEAK`; narrate synthetic Hinglish crisis scenario: *"Mera naam Ramesh hai... gaon wale bol rahe hain ki complaint wapas lo nahi toh ghar jala denge..."* | Citizen Voice Intake (`/intake/voice`) | `SpeechToTextProvider` streaming WebSockets | Low barrier to entry; clear mic states; zero confusing sentiment percentages shown to citizen. |
| **0:45 – 1:10** | **Real-Time Detection** | Live transcript appears; threat keywords highlighted in real-time; synchronized Evidence Timeline pins threat at 00:32. | Operator Live Copilot (`/operator/live`) | `TextSafetyEngine` & `SpeechAnalyticsEngine` | Immediate visual synchronization of audio waveform, transcript, and risk events. |
| **1:10 – 1:30** | **Explainability & 3D Triage** | Show **Immediate Safety: ELEVATED**, **SVI: 74 / HIGH**, **Reported Incident Urgency: CRITICAL**. Click Evidence pin to open Evidence Inspector. | Evidence Inspector Drawer (`/operator/live`) | `MultimodalFusionEngine` | **USP 1 & USP 2:** Explicit separation of safety, vulnerability, and urgency; transparent attribution of SVI score. |
| **1:30 – 1:50** | **Human Co-Pilot Assistance** | Operator reviews AI-suggested trauma-informed question: *"Are you somewhere you feel safe right now?"* Operator clicks `[USE]`. | Suggested Prompt Card (`/operator/live`) | `PromptAdvisoryEngine` | Protocol-backed question templates ensure trauma-informed inquiry without automated unreviewed speech. |
| **1:50 – 2:15** | **Response Orchestration** | System automatically recommends **Tele-MANAS Counseling (High Priority)** and **DLSA Legal Aid (Section 15A Protection)**. Operator approves. | Recommendation Panel (`/operator/live`) | `SupportRecommendationEngine` | Rule-guided support matching based on verified jurisdiction, language, and urgency. |
| **2:15 – 2:35** | **Closed-Loop Verification** | Open Case Journey. Show referral dispatched → Acknowledged by DLSA sandbox → Follow-up task scheduled via `FollowUpPolicy`. | Referral Journey Tracker (`/support/referrals/:id`) | `ReferralLifecycleEngine` | **USP 3:** Solves the "Did help actually arrive?" question through verifiable state tracking and SLA alerts. |
| **2:35 – 2:50** | **Government Outcomes** | Transition to Administrative Outcomes view. Display District Resource Gaps (e.g. low Marathi-speaking counseling capacity). | Resource Gap Analytics (`/admin/resource-gaps`) | `ResourceGapAnalytics` | High-level data intelligence enabling the Ministry to allocate physical social welfare budgets efficiently. |
| **2:50 – 3:00** | **Empirical Evidence** | Open Judge Evidence Center (`/demo/evidence`). Display passing test suites, real latency numbers, model cards, and DPDP compliance. | Judge Evidence Center (`/demo/evidence`) | System Health & Test Telemetry | 100% truth-state disclosure (LIVE vs SANDBOX vs ADAPTER_READY). Zero smoke and mirrors. |

---

## 2. Golden Scenarios Matrix (Mandatory Failure & Edge Cases)

| Scenario ID | Scenario Name | Test Utterance / Input Conditions | Expected Immediate Safety | Expected SVI Band | Expected Reported Urgency | Core System Verification Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SCN-A** | **Calm Voice, Severe Violence** | Complainant speaks in a slow, calm, flat monotone (Pitch F0 normal, zero acoustic distress): *"They came with swords last night, broke my father's leg, and said they will kill my children before sunrise."* | `CRITICAL_REVIEW` | `HIGH` (72–82) | `CRITICAL` | **GOLDEN RULE:** Calm acoustic profile MUST NOT down-rank reported incident urgency or immediate life safety. |
| **SCN-B** | **Explicit Self-Harm Intent** | Caller in severe distress: *"I cannot take this humiliation anymore. I have pesticide in my hand and I am going to drink it right now."* | `CRITICAL_REVIEW` | `CRITICAL` (88–96) | `CRITICAL` | Deterministic safety rule triggers immediate high-priority red alert; Tele-MANAS emergency escalation suggested. |
| **SCN-C** | **Negated Self-Harm Statement** | Caller crying: *"I am terrified and heartbroken by what happened, but I am NOT thinking about killing myself. I have to live for my daughter."* | `NO_IMMEDIATE_SIGNAL` | `MODERATE` (45–55) | `HIGH` | Negation resolver correctly distinguishes distress from self-harm; avoids catastrophic false positive emergency dispatch. |
| **SCN-D** | **Quoted / External Threat** | Caller statement: *"The landlord shouted at me: 'I want you dead and buried by tomorrow!'"* | `ELEVATED` | `HIGH` (65–75) | `HIGH` | Contextual extractor classifies as **Third-Party Intimidation**, NOT self-harm ideation. |
| **SCN-E** | **Silent Distress Ingestion** | Complainant trapped in room with perpetrators; taps: `[Can't Speak Safely]` → `[Unsafe Right Now]` → `[Need Immediate Police & Shelter]`. | `CRITICAL_REVIEW` | `CRITICAL` (85–92) | `CRITICAL` | Discreet tap-based intake executes silently with zero microphone activation and instant Quick Exit redirect. |
| **SCN-F** | **Trilingual Code-Switching** | Mixed Marathi-Hindi-English: *"Sir, police station madhe FIR ghet nahi ahet. They are openly threatening us ki gaon sodun ja. Mala khup tension ahe."* | `REVIEW_RECOMMENDED` | `HIGH` (62–70) | `HIGH` | ASR and NLP correctly parse trilingual narrative without semantic token dropping or hallucinations. |
| **SCN-G** | **Low Audio Quality / Static** | Narrowband 8kHz telephone audio with heavy engine background noise (SNR = 8dB, packet loss). | `INSUFFICIENT_INFORMATION` | `MODERATE` (Wide CI) | Dependent on Text | Affective Signal Engine outputs `LOW_AUDIO_QUALITY_ABSTAIN`; confidence indicator drops; operator prompted for clarification. |
| **SCN-H** | **Complete External LLM Outage** | External LLM API network connection disabled (simulated cloud failure). | `DETERMINISTIC_RULES_LIVE` | `BASELINE_RULE_SVI` | `STATUTORY_RULES_LIVE` | Platform remains 100% operational: local ASR works, deterministic safety rules fire, case intake saves, degraded banner shown. |
