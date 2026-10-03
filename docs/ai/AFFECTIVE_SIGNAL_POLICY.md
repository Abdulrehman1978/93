# SAMBAL AI Policy — Affective Signal & Acoustic Telemetry Specification

> **Packet ID:** PKT-02  
> **Status:** AUTHORITATIVE AI POLICY  
> **Last Updated:** 2026-10-03  
> **Contract Milestone:** Binding Contract for Packet 10 (Acoustic & Affective Signal Engine)  

---

## 1. Foundational Status: Supporting Signal Only

The extraction of emotional and affective cues from human voice (often termed "Emotion AI") is subject to severe scientific, cultural, and demographic variability. Vocal pitch, rate of speech, and tremor vary dramatically across gender, age, regional accents, dialects, background noise, and individual respiratory health.

SAMBAL establishes a binding contract for **Packet 10**:
```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ MANDATORY CLASSIFICATION:          SUPPORTING_SIGNAL_ONLY                   │
│                                                                             │
│ Acoustic and affective signals serve solely as secondary, supportive cues  │
│ to guide frontline operator conversational pacing, listening depth, and     │
│ empathetic phrasing.                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Permitted Affective & Acoustic Signal Categories

The acoustic feature extractor (Packet 10) is restricted to extracting the following objective and supporting parameters:

### 2.1 Low-Level Acoustic Descriptors (LLDs)
1. **Pitch Perturbation (Jitter):** Micro-variations in fundamental frequency (F0), correlating with vocal cord strain.
2. **Amplitude Perturbation (Shimmer):** Micro-variations in vocal intensity.
3. **Harmonics-to-Noise Ratio (HNR):** Ratio of acoustic energy to aspiration noise (roughness/breathiness).
4. **Speech-Pause Dynamics:** Frequency and duration of unvoiced silences (> 1.5s, > 3.0s, > 5.0s), indicating hesitation, crying, or choking on words.
5. **Speech Rate / Tempo:** Syllables per second (rapid pressured speech vs lethargic flat speech).
6. **Energy Arousal:** Root-Mean-Square (RMS) energy distribution.

### 2.2 High-Level Supporting Affective Classifiers
- **`FEAR_ASSOCIATED`:** Rapid speech rate, elevated pitch, high vocal tremor, sudden breathlessness.
- **`SADNESS_ASSOCIATED`:** Low pitch contour, monotonic intonation, prolonged weeping pauses, low energy.
- **`HIGH_AROUSAL`:** Loud volume, sudden pitch spikes, hurried delivery (distress or panic).
- **`DISTRESS_ASSOCIATED`:** Compound presentation of vocal instability and long weeping pauses.
- **`ANXIETY_ASSOCIATED`:** Rapid vocal pace with frequent micro-hesitations.
- **`UNCERTAIN`:** Background noise or poor audio SNR prevents reliable acoustic extraction.

---

## 3. Strict Absolute Prohibitions on Affective Signals

Under zero circumstances may an affective or acoustic signal independently make, trigger, or justify any of the following consequential actions:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ ABSOLUTE PROHIBITIONS ON EMOTION AI / ACOUSTIC SIGNALS:                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✕ CANNOT independently cause an ERSS 112 or police emergency referral.      │
│ ✕ CANNOT independently cause a psychiatric emergency dispatch.              │
│ ✕ CANNOT independently prove or disprove suicidal ideation.                 │
│ ✕ CANNOT determine or modify Reported Incident Urgency (Dimension C).      │
│ ✕ CANNOT establish deception, lying, or "stress due to guilt".             │
│ ✕ CANNOT establish complainant credibility, honesty, or truthfulness.      │
│ ✕ CANNOT override explicit semantic danger statements (Guardrail 1).       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Explanatory Justifications:
1. **Why it cannot determine legal urgency:** A complainant reporting a delayed land dispute who cries hysterically has high emotional distress, but the legal incident urgency is Routine. An emotional voice does not make a civil dispute a criminal emergency.
2. **Why it cannot judge credibility:** The belief that "voice stress analysis" detects deception is scientific fraud thoroughly debunked by the National Research Council. Physiological arousal reflects fear of being disbelieved, trauma recall, or nervousness, NOT mendacity.

---

## 4. Legitimate Operational Utilization

Affective signals may be utilized exclusively for:
1. **Operator Pacing Guidance:** When `FEAR_ASSOCIATED` or `SADNESS_ASSOCIATED` is present, the operator workspace displays gentle pacing suggestions: *"Caller shows high distress cues; consider pausing and allowing unhurried time before asking for administrative details."*
2. **Multi-Modal Triangulation:** Feeding secondary supporting weights into the Packet 11 fusion model where explicit text evidence is already present.
3. **Operator Fatigue Monitoring:** Assisting supervisors in monitoring aggregate call center stress loads during major regional incidents.
