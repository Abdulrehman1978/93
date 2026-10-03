# SAMBAL Responsible AI & Ethical Governance Specification

> **Document ID:** AI-RESPONSIBLE-GOVERNANCE-V2  
> **Status:** MANDATORY & BINDING  
> **Topic:** Ethical Boundaries, Human-in-the-Loop Safeguards, Emergency Dispatch Limits, and Bias Mitigation  
> **Last Updated:** October 2026

---

## 1. Foundational Ethical Mandate

The **SAMBAL Intelligence & Response Layer** is designed to provide trauma-informed decision support and triage assistance to authorized human personnel. It is **NOT** an autonomous legal, clinical, or law enforcement decision maker.

### Absolute Negative Boundaries:
1. **No Psychiatric or Medical Diagnosis:** The system must never claim to diagnose Post-Traumatic Stress Disorder (PTSD), Major Depressive Disorder (MDD), anxiety disorders, or any clinical condition. It outputs *observable distress indicators* to guide human review.
2. **No Truth or Credibility Scoring:** Categorical ban on "Lie Detection", "Truth Probability", "Credibility Index", or "Fake Victim Scores". Voice stress analysis is scientifically discredited for truth detection and systematically discriminates against victims experiencing flat affect or trauma-induced dissociation.
3. **No Demographic or Caste Profiling:** Acoustic features must never be used to infer caste, religion, gender identity, sexual orientation, honesty, morality, or criminality.
4. **No Autonomous Crime / Guilt Determination:** The system assesses **Reported Incident Urgency** and potential support needs. It does **NOT** determine whether an offence is legally proven or whether an accused person is guilty. Legal characterization is an exclusive human/judicial responsibility.

---

## 2. Emergency Adapter & Law Enforcement Boundary

### The Human-Authorized Handoff Principle
Under no circumstances may an AI score, threshold breach, or safety model event autonomously initiate contact with law enforcement, police protection cells, or emergency services (`ERSS 112`), unless a future formally approved government statutory policy explicitly authorizes such autonomous action.

1. **Advisory Function Only:** When acute physical danger or active violence is detected, the **Immediate Safety Gate** emits a high-priority advisory banner (`CRITICAL_REVIEW`) on the 14566 Operator Live Copilot.
2. **Mandatory Human Authorization:** Dispatching an emergency payload to `ERSS112Adapter` or an Atrocity Protection Cell strictly requires the human operator to:
   - Verbally confirm the caller's immediate safety status and physical location.
   - Click an explicit authorization control: `[AUTHORIZE EMERGENCY ESCALATION]`.
   - Log an auditable justification reason.
3. **Harm Prevention Rationale:** Unsolicited or erroneous automated dispatch of police to a vulnerable complainant's village residence can trigger severe retaliation from dominant caste perpetrators, escalate domestic violence, or cause catastrophic harm.

---

## 3. Bounded Affective AI & Counter-Acoustic Overrides

1. **Acoustic Subordination Rule:** Acoustic distress signals serve as bounded supporting evidence (maximum $\pm 15$ points SVI). Explicit textual narratives of violence, threats, or weapons strictly outrank acoustic classifications.
2. **Calm Caller Protection:** If a complainant describes an active threat in a calm, flat, or dissociated tone of voice, the system must prioritize **Reported Incident Urgency: CRITICAL** and elevate the **Immediate Safety Gate**, completely ignoring the low acoustic arousal.
3. **Abstention on Degradation:** If telephone audio quality drops below 10dB SNR or exhibits significant packet clipping, affective models must emit `LOW_AUDIO_QUALITY_ABSTAIN` and downstream confidence intervals must widen.

---

## 4. Model Registry & Audit Lineage

Every AI model deployed within SAMBAL must be registered with:
- Model Name, Provider, Version, and License.
- Explicit Task Scope and Documented Known Failure Modes.
- Evaluation Metrics across supported Indian languages (Hindi, English, Marathi, Bengali, Tamil, Telugu).
- Defined degraded-mode fallback path.
- Immutable log entry on every inference run referencing the model version and policy version.
