# SAMBAL Product Policy — Resource Routing & Support Allocation

> **Packet ID:** PKT-02  
> **Status:** AUTHORITATIVE POLICY  
> **Last Updated:** 2026-10-03  
> **Traceability:** SIH26093 Resource Allocation & Ethical AI Requirements  

---

## 1. Principle of Transparent & Objective Routing

In a public welfare and justice system serving marginalized communities, algorithmic opacity and biased resource distribution can reinforce existing caste inequalities. 

SAMBAL enforces **Transparent, Auditable, and Objective Routing**:
- Every service referral recommendation must be explainable in plain terms.
- Routing decisions must be based strictly on legitimate operational criteria.
- Any attempt to use discriminatory, speculative, or unscientific profiling is fundamentally prohibited by system architecture.

---

## 2. Permitted Routing Criteria

The matching engine may evaluate ONLY the following 9 objective factors:

```mermaid
graph TD
    CitizenInput[Citizen Need & Context] --> Evaluator{Objective Matching Engine}
    
    Evaluator --> C1[1. Service Need: Matched from Taxonomy]
    Evaluator --> C2[2. Urgency Level: Routine / Priority / Urgent / Critical]
    Evaluator --> C3[3. Administrative Jurisdiction: State / District / Taluka]
    Evaluator --> C4[4. Language & Dialect Compatibility]
    Evaluator --> C5[5. Provider Operational Availability]
    Evaluator --> C6[6. Verified Capacity: If Empirical Data Exists]
    Evaluator --> C7[7. Accessibility Requirements: Assistive / Silent / Screen Reader]
    Evaluator --> C8[8. Citizen Express Preference: Opt-in / Opt-out]
    Evaluator --> C9[9. Statutory Policy Mandates: E.g. PoA Rules 12 & 15]
    
    Evaluator --> Recommendation[Ranked Support Referral Candidates]
```

### Detailed Criterion Definitions:
1. **Service Need:** Exact match between the elicited grievance need and the service taxonomy (e.g. physical injury matches `MEDICAL_ASSISTANCE`; trauma recall matches `COUNSELLING`).
2. **Reported Incident Urgency:** Higher urgency matches providers with faster operational response times (e.g. `CRITICAL` matches 24/7 emergency desks; `ROUTINE` matches standard legal aid clinics).
3. **Administrative Jurisdiction:** Strict geographic alignment with the citizen's location (District, Sub-Division, Taluka) to ensure statutory officers under the PoA Act have legal jurisdiction.
4. **Language & Dialect Compatibility:** Matches the complainant's spoken or preferred language with providers capable of native communication (e.g. Marathi speaker routed to Maharashtra DLSA panel lawyer).
5. **Operational Availability:** Evaluates verified current operational status (`VERIFIED_CURRENT`, open office hours, active helpline shift).
6. **Verified Capacity (Strict Standard):** Capacity may ONLY be factored in if direct, real-time API or verified data exists (e.g. shelter bed counts). The system MUST NOT estimate or fabricate hypothetical capacity metrics.
7. **Accessibility Requirements:** Specialized routing for complainants with hearing/speech disabilities (routing to text/silent queues or sign language interpreters) or low literacy (voice/telephony preference).
8. **Citizen Express Preference:** The complainant's explicit choice overrides algorithmic ranking (e.g. complainant requests an NGO legal clinic rather than government legal services).
9. **Statutory Policy Mandates:** Enforces statutory guidelines (e.g. Section 15A of PoA Act mandating free travel and maintenance allowance for victims attending proceedings).

---

## 3. Explicitly Prohibited Routing Criteria

The system architecture and routing logic STRICTLY FORBID factoring in, collecting, or optimizing for:

| Prohibited Criterion | Why it is Forbidden | Architectural Enforcement |
| :--- | :--- | :--- |
| **Caste Inference from Voice / Surnames** | Highly discriminatory, inaccurate, unscientific, and offensive. | Voice models do NOT output sub-caste predictions. Demographics are self-reported only. |
| **Acoustic Voice Profiling / Tone** | Pitch, timber, or accent must not determine resource allocation. | Acoustic signals are restricted to `SUPPORTING_SIGNAL_ONLY` for operator empathy pacing. |
| **Algorithmic "Credibility" or "Honesty" Scores** | "Lie detection" via voice/text is pseudoscience and violates fundamental justice. | Prohibited by policy; zero deception metrics exist in contracts or code. |
| **Social Worth / Educational Status** | Reinforces caste hierarchies and administrative elitism. | Completely excluded from data models and scoring. |
| **"Likelihood to Cooperate" Scores** | Traumatized victims often withdraw; penalizing them deprives them of essential care. | System does not calculate recidivism or cooperation probabilities. |

---

## 4. Resolving Resource Bottlenecks & No-Resource Scenarios

When no verified provider is available in the citizen's district (e.g. zero psychiatric social workers in a rural district):
1. **No Silent Failure:** The system shall NEVER silently swallow an unmet need or log it as resolved.
2. **Vertical Escalation:** The referral automatically escalates to the **State Social Justice Nodal Desk** for interstate/interdistrict resource allocation.
3. **Telephony Bridge:** If local physical providers are absent, the system routes to national digital/telephony helplines (Tele-MANAS 14416 or NALSA 15100).
4. **Resource Gap Analytics:** The unmet referral is permanently logged into the **District Resource Gap Analytics Dashboard** (Packet 22), highlighting the deficit for Ministry leadership.
