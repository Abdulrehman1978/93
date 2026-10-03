# Official Product Claims Register
## Empirical Verification, Truthful Status Classifications & Operational Limitations

> **Document ID:** CLAIMS-REGISTER-V2  
> **Standard:** Mandatory empirical verification for all product, performance, security, and algorithmic claims. Zero unsupported claims.  
> **Evaluation Date:** 2026-10-03 (Updated for Packet 02R Remediation)  
> **Truth Status Vocabulary:**
> - `DESIGN_POLICY` (Architectural or design standard enforced by policy; pending downstream implementation)
> - `READINESS_TARGET` (Preparation for phased statutory or regulatory frameworks)
> - `PILOT_TARGET` (Operational target for initial deployment; subject to empirical tuning)
> - `RESEARCH_BENCHMARK` (Scientific literature baseline)
> - `STATUTORY` (Directly mandated by Indian statutory enactment or judicial authority)
> - `OFFICIAL_SOURCE` (Verified against current published government baselines)
> - `IMPLEMENTED` (Code and automated tests active in repository)
> - `MEASURED` (Empirically benchmarked and verified with recorded metrics)

---

## 1. Verified Product Claims Table

| Claim ID | Product Claim Statement | Claim Category | Truth Status | Source Reference | Automated Test / Verification | Documented Operational Limitation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CLM-01` | "Sub-1.5 second real-time transcription latency on Indian English and Hindi audio." | Speech / ASR | `RESEARCH_BENCHMARK` | `faster-whisper-turbo` (CTranslate2 INT8) on 4-core CPU. | `tests/test_asr.py` (Packet 08) | Narrowband 8kHz audio with SNR < 10dB may increase latency; formal benchmarking deferred to Packet 08. |
| `CLM-02` | "Zero false-negative safety design philosophy for explicit present-tense suicidal intent in Golden Corpus." | Safety / Ethics | `INTERNAL_SAFETY_TARGET` | `docs/ai/GOLDEN_SAFETY_CORPUS.md` | `tests/test_safety_gate.py` (Packet 11) | Abstract metaphorical poetry without explicit harm tokens requires human operator disambiguation. 0% is a safety goal, not an empirical claim prior to benchmarking. |
| `CLM-03` | "Disambiguates negated self-harm phrases without triggering false alarms." | NLP / Context | `DESIGN_POLICY` | `docs/ai/GOLDEN_SAFETY_CORPUS.md` | `tests/test_text_safety.py` (Packet 09) | Complex double negations in unstandardized vernacular dialects are routed to human review. |
| `CLM-04` | "Calm speech describing severe violence is correctly flagged as CRITICAL URGENCY." | Assessment / Triage | `DESIGN_POLICY` | `docs/product/ASSESSMENT_MODEL.md` | `tests/test_svi_fusion.py` (Packet 11) | Requires complainant to articulate at least one factual indicator of threat, weapon, or injury. |
| `CLM-05` | "Closed-loop tracking monitors referral status from dispatch to verified support delivery." | Operations / Redressal | `DESIGN_POLICY` | `docs/product/REFERRAL_STATE_MACHINE.md` | `packages/contracts/src/index.ts` | Dual confirmation is the gold standard; system supports document and provider confirmation to prevent permanent operational deadlocks. |
| `CLM-06` | "Architecture designed for phased DPDP readiness and privacy-by-design baseline." | Privacy / Legal | `READINESS_TARGET` | Notification S.O. 5042(E) (13 Nov 2025). | `docs/privacy/PROCESSING_PURPOSE_REGISTER.md` | Substantive operational DPDP sections (notice, consent, fiduciary duties) commence in May 2027. System is DPDP-ready, not claiming non-commenced sections are currently binding positive law. |
| `CLM-07` | "Core emergency intake operates uninterrupted during complete cloud LLM failure." | Resilience / SRE | `DESIGN_POLICY` | `docs/product/GOLDEN_SCENARIOS.md` (Scenario H) | `tests/test_degraded_mode.py` (Packet 16) | Rich semantic summaries and counterfactual explanations are disabled in offline degraded mode. |
| `CLM-08` | "Conforms to GIGW 3.0 and WCAG 2.1 AA accessibility standards." | Accessibility / UX | `MEASURED` | Axe-core automated scan in Playwright CI (Run `37097932370`). | `apps/web/tests/e2e/smoke.spec.ts` | High-density operator live triage requires minimum 1024px viewport width for optimal panel visibility. |
| `CLM-09` | "Ephemeral audio streaming doctrine — zero default raw audio disk persistence." | Privacy / Architecture | `DESIGN_POLICY` | `docs/privacy/DATA_MINIMIZATION.md` | `docs/product/DATABASE_SEMANTICS_HANDOFF.md` | Audio streamed in volatile memory; raw audio retention requires explicit unbundled consent or court order, tracked through multi-stage deletion states. |
| `CLM-10` | "Quick Exit initiates immediate local browser navigation away from sensitive forms." | Safety / UX | `PILOT_TARGET` | `docs/product/TRAUMA_INFORMED_UX.md` | `apps/web/tests/e2e/smoke.spec.ts` | Target is immediate local initiation; cannot wipe external network ISP logs, DNS caches, OS screenshots, or stalkerware keyloggers. |
| `CLM-11` | "Free legal aid is a statutory right for Scheduled Caste and Scheduled Tribe citizens." | Legal / Statutory | `STATUTORY` | Section 12(b), Legal Services Authorities Act, 1987. | `docs/product/SERVICE_TAXONOMY.md` | Free legal aid entitlement is statutory; advocate empanelment quality is managed by jurisdictional DLSAs. |
| `CLM-12` | "Atrocity victims are entitled to interim cash or kind relief within 7 days." | Legal / Statutory | `STATUTORY` | Rule 12(4), SC/ST (PoA) Rules, 1995. | `docs/SOURCE_REGISTRY.md` (Entry 7) | Binding on District Magistrate/Administration; SAMBAL tracks compliance milestones without claiming administrative executive power. |
| `CLM-13` | "Prototype adheres to State Emblem Act 2005 by utilizing neutral generic service icons." | Branding / Legal | `DESIGN_POLICY` | State Emblem of India (Prohibition of Improper Use) Act, 2005. | `docs/product/TRAUMA_INFORMED_UX.md` | State emblem is strictly reserved for authorized government entities; prototype does not falsely claim government status. |
| `CLM-14` | "Tele-MANAS integration provides 24/7 mental health access in 20 languages via 53 cells." | Service / Health | `OFFICIAL_SOURCE` | Tele-MANAS Published National Directory (MoHFW/NIMHANS). | `docs/SOURCE_REGISTRY.md` (Entry 2) | Current integration pattern is `ADAPTER_READY` (simulated telephony handoff); zero false claims of unauthorized live API access. |
