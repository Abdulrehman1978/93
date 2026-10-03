# SAMBAL Product Guide — Citizen Content & Trauma-Informed Copy

> **Packet ID:** PKT-02  
> **Status:** AUTHORITATIVE CONTENT SPECIFICATION  
> **Last Updated:** 2026-10-03  
> **Traceability:** Civic Calm Design System, Trauma-Informed Communication Standards  

---

## 1. Principles of Trauma-Informed Citizen Copy

Language creates reality. In a crisis portal or helpline interface used by citizens who have faced acute physical, sexual, or social violence, poor phrasing can trigger panic, re-traumatization, alienation, or false security.

All citizen-facing copy across the web shell, mobile PWA, IVR prompts, and SMS confirmations must adhere to three foundational principles:
1. **Absolute Honesty Without False Guarantees:** Never offer false promises of safety or outcome certainty.
2. **Transparent Agency & Control:** Always frame actions around citizen choice (*"You can choose...", "If you wish..."*).
3. **Radical Plain Language:** Eliminate bureaucratic, medical, and algorithmic jargon completely.

---

## 2. The Prohibited vs Preferred Copy Register

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ STRICTLY PROHIBITED PHRASES (ZERO-TOLERANCE COPY VIOLATIONS)               │
├─────────────────────────────────────────────────────────────────────────────┤
│ ✕ "AI diagnosed you with PTSD / Depression."                                │
│ ✕ "We know exactly how you feel."                                           │
│ ✕ "You are completely safe now."                                            │
│ ✕ "Your case will definitely result in compensation / conviction."          │
│ ✕ "Your voice proves you are lying / distressed."                           │
│ ✕ "System calculated your risk score as 85%."                               │
│ ✕ "Emergency police have been dispatched to your house automatically."      │
│ ✕ "You must answer this question to proceed." (Forced disclosure)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Table of Canonical Conversions

| Context | Prohibited Phrasing (Unacceptable) | Preferred Trauma-Informed Phrasing (Approved) | Rationale |
| :--- | :--- | :--- | :--- |
| **Intake Greeting** | *"Welcome to the automated AI grievance processing engine."* | *"You are connecting with SAMBAL. We are here to listen and help connect you with verified support."* | Human-centric, warm, non-mechanistic. |
| **Safety Assessment** | *"AI detected high danger. You are not safe."* | *"Based on what you shared, our team wants to make sure you have immediate safety support. A trained operator is reviewing your case."* | Grounded in citizen testimony, not machine omniscience. |
| **Mental Health Referral** | *"Our algorithms detected clinical depression. You need psychological treatment."* | *"Experiencing harassment can take a heavy emotional toll. If you wish, we can connect you with a supportive counsellor at Tele-MANAS."* | Voluntary, non-stigmatizing, non-diagnostic. |
| **False Reassurance** | *"Don't worry, you are 100% safe now."* | *"We take your safety seriously. Let's look at what protective options are available to you right now."* | Truthful; avoids gaslighting a victim whose house is still under threat. |
| **Acoustic / Voice Cues** | *"Your voice indicates 80% stress and tremor."* | *(NEVER DISPLAYED TO CITIZEN)* | Machine telemetry has zero citizen utility and induces anxiety. |
| **Legal Status** | *"We will ensure the accused is arrested under Section 3 of the PoA Act."* | *"We can connect you with a free legal aid lawyer from NALSA to assist you with your police complaint and legal rights."* | Respects statutory separation of powers. |
| **Questioning** | *"Answer all questions or your complaint will be rejected."* | *"You can share as much or as little as you feel comfortable with right now. You can pause at any time."* | Non-coercive; honors citizen autonomy. |
| **Silent Mode Exit** | *"Click here to abort application session."* | *"Quick Exit — Leave page immediately."* | Clear, instant, life-protective. |

---

## 3. Microcopy Rules for Key Surfaces

### 3.1 Citizen Channel Selection
```text
[ SPEAK ]   Talk to us in your own language. We will listen and take down your words.
[ WRITE ]   Type your grievance quietly at your own pace.
[ SILENT ]  Tap discreet options if you cannot make noise or are in danger.
```

### 3.2 Quick Exit Button
- Position: Top-right corner of every screen, persistently visible in Silent Mode.
- Label: `QUICK EXIT [ESC]`
- Action: Instantly redirects browser to a neutral government public website (e.g. `india.gov.in` or weather portal) and purges session storage / active form cache.

### 3.3 Status Confirmation Message
```text
"Your grievance has been received.
Your tracking number is: [S-2026-9032].
A trained helpline officer is reviewing your information.
You do not need to do anything else right now."
```
