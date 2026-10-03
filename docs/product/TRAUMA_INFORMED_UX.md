# SAMBAL Product Specification — Trauma-Informed UX & Civic Calm Design System
## Foundational UX Philosophy, Civic Calm Tokens, Concealment Truth & Branding Limits

> **Packet ID:** PKT-02R  
> **Status:** AUTHORITATIVE UX SPECIFICATION  
> **Evaluation Date:** 2026-10-03  
> **Traceability:** Civic Calm Design System Tokens, GIGW 3.0 / WCAG 2.1 AA Standards  
> **Policy Source Classes:** `INTERNAL_SAFETY_POLICY` (UX Safety) / `STATUTORY` (State Emblem Act 2005 compliance)

---

## 1. Foundational Philosophy: Civic Calm

Trauma is not merely an emotional memory; it is a profound neurobiological state. When an individual experiences systemic caste violence, threat of physical harm, or severe institutional betrayal, their nervous system enters high sympathetic arousal (fight, flight, freeze, or fawn).

In this state:
- Working memory is severely constricted.
- Ambiguous or bureaucratic language induces intense suspicion and withdrawal.
- Aggressive visual stimuli (harsh red banners, blinking countdowns, loud alert sounds) trigger panic and acute re-traumatization.

SAMBAL establishes the **Civic Calm Design System**—a trauma-informed user experience standard engineered specifically for public welfare and crisis intervention interfaces.

---

## 2. The 5 Pillars of Trauma-Informed UX

```mermaid
graph TD
    Root[5 Pillars of Trauma-Informed UX] --> P1[1. Physical & Emotional Safety]
    Root --> P2[2. Trustworthiness & Transparency]
    Root --> P3[3. Peer Support & Collaboration]
    Root --> P4[4. Empowerment, Voice & Choice]
    Root --> P5[5. Cultural, Gender & Caste Humility]
```

### Pillar 1: Physical & Emotional Safety
- **Physical Concealment:** The Silent Distress mode and Quick Exit mechanisms protect the user from physical retaliation by perpetrators who may be in the same dwelling.
- **Predictable Interactions:** Every screen clearly indicates what will happen next before an action is taken. Zero unexpected popups, zero sudden audio blares.
- **Safe Tone:** Interfaces never scold, reprimand, or display harsh validation errors (e.g. replacing red *"INVALID INPUT"* with gentle *"Please check this phone number"*).

### Pillar 2: Trustworthiness & Transparency
- **No Deceptive Dark Patterns:** The system never tricks users into surrendering data or forces consent bundling.
- **Clarity on AI Presence:** Citizens are told clearly: *"This tool helps our human team understand your words faster. A trained person makes all final decisions."*
- **Visible Privacy Boundaries:** Explicitly discloses who will see the complaint before the citizen clicks submit.

### Pillar 3: Peer Support & Collaboration
- **Warm, Non-Hierarchical Tone:** Replaces cold bureaucratic phrasing with empathetic, respectful language.
- **Supportive Pacing:** The interface allows citizens to pause, save drafts, and resume when they feel emotionally ready.

### Pillar 4: Empowerment, Voice & Choice
- **Channel Autonomy:** Citizens choose how to communicate: Speak, Write, or Tap silently.
- **Voluntary Disclosures:** Questions are framed non-coercively; users can skip traumatic details without forfeiting access to basic emergency protection.
- **Reversible Decisions:** Citizens can revoke referral consent or change preferred contact channels at any time.

### Pillar 5: Cultural, Gender & Caste Humility
- **Dignified Representation:** Avoids patronizing, stereotyping, or victim-blaming imagery.
- **Language Inclusivity:** Native script support with colloquial and dialectal tolerance; never scolds for grammatical non-standard speech.

---

## 3. Visual & Sensory Architecture (Civic Calm Tokens)

### 3.1 Color Palette Governance
The interface strictly avoids hyper-saturated, anxiety-inducing primary colors:

| Token Name | Hex Code | Purpose | Emotional Impact |
| :--- | :---: | :--- | :--- |
| `--color-surface-calm` | `#F8FAFC` | Main application background | Serene, neutral, low visual glare |
| `--color-text-primary` | `#0F172A` | Primary typography | High contrast (14.2:1 against surface), maximum legibility |
| `--color-text-secondary`| `#475569` | Supporting explanations | Gentle, readable, non-distracting |
| `--color-civic-teal` | `#0D9488` | Primary interactive buttons | Trust, steady guidance, non-alarming |
| `--color-soft-amber` | `#D97706` | Warning / Review Recommended | Attention without panic |
| `--color-cardinal-alert`| `#DC2626` | Operator-only emergency banner | High visibility; **STRICTLY FORBIDDEN on citizen screens** |

### 3.2 Strict Prohibition on Citizen Distress Badges
- **Zero Red Badges for Citizens:** The citizen UI shall NEVER display red alert boxes saying *"CRITICAL RISK"*, *"HIGH VULNERABILITY"*, or *"DANGER LEVEL 90%"*. Such displays induce extreme panic in victims.
- **Calm Reassurance Banners:** On the citizen side, an elevated case displays a reassuring blue/teal banner:
  > *"We have received your grievance. Because of the urgent nature of what you shared, our senior team has been notified to assist you quickly."*

---

## 4. Emergency Concealment & Quick Exit Standards

### 4.1 Quick Exit Mechanism
- **Visibility:** Present on all citizen-facing pages, pinned permanently in the top-right corner.
- **Trigger:** Single tap or click, or keyboard shortcut (`ESC` key).
- **Execution Target:** `DESIGN_TARGET: immediate local navigation initiation` (actual end-to-end rendering and redirect latency to be formally benchmarked in Packet 29).
- **Client Actions:**
  1. Window immediately navigates via `window.location.replace` to an innocuous, high-traffic public portal (e.g. weather or general public utility portal).
  2. Clears browser `sessionStorage`, active uncommitted form state, and DOM input fields.
  3. Replaces browser history state so the browser "Back" button does not return to the complaint form.

### 4.2 Documented Technical Limitations of Quick Exit
The platform documents the following real-world technical boundaries so users and operators maintain truthful expectations:
- **Outside Controlled Scope:** Quick Exit cannot purge browser history entries generated *prior* to entering the application or outside controlled navigation hooks.
- **Network-Level Footprints:** Quick Exit cannot remove local DNS cache entries, Wi-Fi router query logs, or ISP-level connection logs.
- **Operating System Footprints:** Does not wipe OS-level recent application activity, screenshot caches, clipboard history, or mobile app switcher preview cards.
- **Device Spyware / Keyloggers:** Cannot conceal activity if the abuser has installed stalkerware, keyloggers, or hardware screen capture on the device.
- **Submitted Data:** Quick Exit purges client state, but cannot delete records that have already been transmitted to and acknowledged by the server.

### 4.3 Silent Distress Mode & Neutral Branding Standards
- **Discreet Title:** Browser tab title displays *"Citizen Information Services"*.
- **Neutral Generic Service Icon:** Uses a neutral, stylized civic icon (e.g. geometric leaf or abstract shield).
- **Strict Prohibition on State Emblem in Prototype:**
  Under the State Emblem of India (Prohibition of Improper Use) Act, 2005, the Lion Capital of Asoka and national emblem symbols are strictly reserved for official government entities. The prototype must **never** use the State Emblem in favicons or headers, ensuring it does not falsely imply official government status or endorsement prior to formal administrative authorization.
- **No Sound Emission:** All HTML5 audio tags and Web Audio API contexts are explicitly muted by default.
