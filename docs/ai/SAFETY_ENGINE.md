# Safety Engine & Immediate Safety Gate Architecture

> **Document ID:** AI-SAFETY-ENGINE-SPEC-V2  
> **Topic:** Multi-Layer Safety Architecture, Self-Harm Detection, and Human Emergency Boundary  
> **Status:** APPROVED

---

## 1. Multi-Layer Safety Architecture

The safety engine protects callers and ensures critical signals are caught instantaneously without relying on unpredictable external cloud models:

```text
Incoming Transcript / Narrative
              │
              ▼
[ LAYER 1: DETERMINISTIC MULTILINGUAL SAFETY RULES ]  ◄── Latency < 1ms; 100% Offline
├── Regex patterns & exact lexicons (Hindi, Marathi, Bengali, Tamil, Telugu, English)
├── Matches: Imminent suicide intent, active weapons, acute physical assault
├── IF MATCH: Triggers Immediate Safety Gate (`CRITICAL_REVIEW`)
              │
              ▼
[ LAYER 2: SEMANTIC THREAT & NEGATION CLASSIFIER ]    ◄── Latency < 40ms; ONNX Transformer
├── Disambiguates complex negations ("I am NOT thinking of killing myself")
├── Disambiguates quoted threats ("He told me he will burn our house")
├── Classifies intimidation, coercion, social boycott, and retaliation
              │
              ▼
[ LAYER 3: CONTEXTUAL NARRATIVE REASONER ]             ◄── Latency < 1.2s; Pydantic Schema
├── Synthesizes structural vulnerability, dependency, and safe housing access
├── Evaluates temporal status (active ongoing vs historical event)
              │
              ▼
[ LAYER 4: HUMAN AUTHORIZATION & WORKFLOW GATE ]       ◄── NON-NEGOTIABLE
├── 14566 Operator verifies immediate danger and location
└── High-impact referral (ERSS 112, Police Atrocity Cell) strictly requires human click
```

---

## 2. Emergency Adapter & Law Enforcement Boundary

1. **Non-Autonomous Handoff Rule:** Under no circumstances may the Safety Engine autonomously dispatch police, emergency responders (`ERSS 112`), or witness protection teams based on AI detection alone.
2. **Advisory Alerts Only:** The engine presents an immediate high-priority visual alert on the Operator Live Copilot:
   - High-contrast red alert banner.
   - Exact highlighted phrase that triggered the gate.
   - Suggested trauma-informed safety questions (e.g. *"Are you somewhere safe right now?"*).
   - One-click human authorization control to dispatch to `ERSS112Adapter`.
3. **Audit Logging:** Every human acceptance, dismissal, or modification of a safety alert is recorded in the immutable audit log with operator ID, timestamp, and justification.

---

## 3. Self-Harm & Suicide Prevention Taxonomy

The engine enforces a rigorous separation between active imminent intent and non-acute distress:

| Category | Linguistic Examples (Hindi / English / Marathi) | Immediate Safety State | System Action |
| :--- | :--- | :--- | :--- |
| **Imminent Present-Tense Intent** | "I am going to drink poison right now." / "Main abhi zeher peene ja raha hoon." / "Mee aata aatmahatya karnar ahe." | `CRITICAL_REVIEW` | Instant high-priority alert; Tele-MANAS emergency protocol suggested; operator prompted to verify safety. |
| **Negated Self-Harm Statement** | "I am heartbroken, but I am NOT thinking of killing myself." / "Main aatmahatya ke baare mein nahi soch raha." | `NO_IMMEDIATE_SIGNAL` | Evaluated as psychological distress only; avoids false positive emergency dispatch. |
| **Historical Ideation / Past Trauma** | "Three years ago I thought about suicide after my brother died." / "Pehle main aisi baatein sochta tha." | `REVIEW_RECOMMENDED` | Flagged as contextual vulnerability factor; does not trigger acute emergency alarm. |
| **Third-Party / Quoted Threat** | "The accused shouted that he will kill me." / "Usne bola main tujhe jaan se maar doonga." | `ELEVATED` | Classified under **External Threat / Intimidation**, NOT self-harm. |
