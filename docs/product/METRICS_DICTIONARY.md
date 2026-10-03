# SAMBAL Product Specification — Authoritative Metrics Dictionary
## Target Classifications, Outcome Benchmarks & Algorithmic Safety Philosophy

> **Packet ID:** PKT-02R  
> **Status:** AUTHORITATIVE SPECIFICATION  
> **Evaluation Date:** 2026-10-03  
> **Traceability:** SIH26093 Redressal Impact & Responsible AI Evaluation  
> **Target Classification Taxonomy:** Every metric target is explicitly classified as one of:
> - `STATUTORY_REQUIREMENT` (Mandated by Indian law or statutory rules)
> - `OFFICIAL_SERVICE_SLA` (Established by formal partner service agreement)
> - `INTERNAL_SAFETY_TARGET` (Design objective for safety guardrails; measured post-implementation)
> - `PILOT_TARGET` (Operational baseline for pilot evaluation; subject to empirical tuning)
> - `RESEARCH_BENCHMARK` (Scientific literature baseline for Indic NLP/speech analytics)
> - `OBSERVATION_ONLY` (Statistical tracking metric; no normative pass/fail threshold)

---

## 1. Principles of Measurement

Traditional AI systems report superficial metrics like *"Model Accuracy = 98.5%"*, which conceal catastrophic real-world failures (e.g. missing a single critical suicide utterance in an imbalanced dataset).

SAMBAL enforces **Outcome-Centric & Safety-First Evaluation**:
1. **Zero-Tolerance for Critical Life-Safety False Negatives:** Missing an imminent self-harm or violent siege signal is treated as an existential system defect. This is an **`INTERNAL_SAFETY_TARGET` and core design philosophy**, not an empirical claim of measured 0% FN performance prior to Packet 08/11 testing.
2. **Support Delivery as the Primary Benchmark:** The success of the system is measured by whether verified assistance reached the citizen, not how many tokens the LLM generated.
3. **Transparent Uncertainty Over False Confidence:** The system is rewarded for abstaining and escalating to humans when data is noisy or ambiguous.

---

## 2. Citizen & Service Outcome Metrics

These metrics quantify real-world public welfare delivery under the MoSJE / NHAA mandate:

| Metric Identifier | Metric Name | Definition & Formula | Target Benchmark | Target Classification |
| :--- | :--- | :--- | :--- | :--- |
| `METRIC_T_REVIEW` | **Time to Human Review** | Duration from citizen intake submission to live human operator queue pickup. | **< 15 sec** (Urgent/Critical)<br/>**< 60 sec** (Routine) | `INTERNAL_SAFETY_TARGET` |
| `METRIC_T_REFERRAL` | **Time to Referral Dispatch** | Duration from intake pickup to transmission of consented referral packet. | **< 10 min** (Immediate needs)<br/>**< 2 hours** (Standard) | `PILOT_TARGET` |
| `METRIC_ACK_RATE` | **Referral Acknowledgement Rate** | Percentage of sent referrals electronically acknowledged by external provider within SLA. | **> 98.0%** | `PILOT_TARGET` |
| `METRIC_ACK_LATENCY`| **Acknowledgement Latency** | Time taken by partner agency (Tele-MANAS, NALSA) to confirm receipt of handoff dossier. | **< 15 min** (Crisis)<br/>**< 4 hours** (Standard) | `PILOT_TARGET` |
| `METRIC_T_FIRST_CONTACT`| **Time to First Support Contact**| Duration from referral dispatch to documented human-to-human contact between provider and victim. | **< 2 hours** (Crisis)<br/>**< 24 hours** (Standard) | `PILOT_TARGET` |
| `METRIC_SVC_START_RATE` | **Service Start Rate** | Percentage of accepted referrals that actively initiate tangible service (Level 4+). | **> 85.0%** | `PILOT_TARGET` |
| `METRIC_FOLLOWUP_RATE` | **Verified Follow-up Rate** | Percentage of active cases where dual-confirmed follow-up is achieved (Level 5+). | **> 80.0%** | `PILOT_TARGET` |
| `METRIC_UNMET_NEED` | **Unmet Support Need Rate** | Referrals stalled or unfulfilled due to provider capacity/availability deficits. | **< 5.0%** | `INTERNAL_SAFETY_TARGET` |

---

## 3. AI & Model Quality Metrics

These metrics evaluate machine learning safety, linguistic robustness, and algorithmic fairness:

| Metric Identifier | Metric Name | Definition & Formula | Target Benchmark | Target Classification |
| :--- | :--- | :--- | :--- | :--- |
| `METRIC_ASR_WER` | **ASR Word Error Rate** | Edit distance between reference human transcript and ASR hypothesis. | **< 12.0%** (Quiet speech)<br/>**< 18.0%** (8kHz telephony) | `RESEARCH_BENCHMARK` |
| `METRIC_CRITICAL_RECALL`| **Critical Phrase Recall** | Percentage of acute distress/danger phrases correctly detected in audio/text streams. | **> 99.5%** | `INTERNAL_SAFETY_TARGET` |
| `METRIC_SAFETY_FN` | **Safety False Negative Rate** | Percentage of true `CRITICAL_REVIEW` or `ELEVATED` cases misclassified as `NO_IMMEDIATE_SIGNAL`. | **0.0% Philosophy** (Empirical rate measured in P08/P11) | `INTERNAL_SAFETY_TARGET` |
| `METRIC_SAFETY_FP` | **Safety False Positive Rate** | Percentage of non-dangerous utterances flagged as Tier-1 emergency interruptions. | **< 3.0%** | `PILOT_TARGET` |
| `METRIC_ABSTENTION_RATE`| **Model Abstention Rate** | Percentage of inputs where model declares `INSUFFICIENT_INFORMATION` rather than guessing. | **Expected 5–10%** in noisy telephony | `OBSERVATION_ONLY` |
| `METRIC_OVERRIDE_RATE` | **Human Operator Override Rate**| Percentage of AI-assigned SVI bands or safety states modified by human operators. | **Expected 8–15%** | `OBSERVATION_ONLY` |
| `METRIC_TRANSLATION_ERR`| **Translation Semantic Error Rate**| Meaning reversals or negation dropouts during Indic-to-English translation. | **< 1.0%** | `INTERNAL_SAFETY_TARGET` |
| `METRIC_LANG_UNCERTAINTY`| **Language Uncertainty Frequency**| Percentage of calls where mixed dialect or code-switching triggers fallback verification. | **Tracked** (No cutoff) | `OBSERVATION_ONLY` |

---

## 4. Operational & Institutional Health Metrics

These metrics monitor queue health, administrative responsiveness, and institutional compliance:

| Metric Identifier | Metric Name | Definition & Purpose | SLA / Threshold | Target Classification |
| :--- | :--- | :--- | :--- | :--- |
| `METRIC_QUEUE_AGE` | **Average Queue Waiting Time** | Current age of oldest unassigned case in the intake triage queue. | **< 30 seconds** | `PILOT_TARGET` |
| `METRIC_URGENT_BACKLOG`| **Unreviewed Urgent Case Count**| Number of `URGENT` or `CRITICAL` cases awaiting supervisor sign-off > 10 min. | **ZERO** (Escalation alert) | `INTERNAL_SAFETY_TARGET` |
| `METRIC_REFERRAL_BACKLOG`| **Provider Referral Backlog** | Number of cases waiting > 48 hours for partner agency initial contact. | **< 10 cases / district** | `PILOT_TARGET` |
| `METRIC_POA_RELIEF_COMPLIANCE`| **PoA Rule 12(4) Relief SLA Compliance**| Percentage of atrocity victims receiving interim relief within statutory 7 days. | **100.0%** | **`STATUTORY_REQUIREMENT`** (Rule 12(4), SC/ST PoA Rules 1995) |
