# Research Provenance & Official Source Registry

> **Document ID:** RESEARCH-PROVENANCE-REGISTRY-V2  
> **Topic:** Master Source Registry and Citations for SIH26093  
> **Last Verified:** October 2026  
> **Standard:** Complete source attribution for all legal, clinical, technological, and architectural assertions

---

## 1. Statutory & Government Sources

| Source Identifier | Title & Official Issuing Body | Date / Reference | Direct Relevance to SAMBAL Architecture |
| :--- | :--- | :--- | :--- |
| `SRC-GOV-01` | **The Protection of Civil Rights Act, 1955** (Act No. 22 of 1955) — Ministry of Law & Justice | 1955 (Amended 1976) | Foundational anti-discrimination statute enforcing constitutional abolition of untouchability (Article 17). |
| `SRC-GOV-02` | **The Scheduled Castes and the Scheduled Tribes (Prevention of Atrocities) Act, 1989** (Act No. 33 of 1989) — Parliament of India | 1989 (Amended 2015, 2018) | Core legal framework governing atrocity offences, Special Courts, and Section 15A rights of victims and witnesses. |
| `SRC-GOV-03` | **Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Amendment Rules, 2016** — Gazette of India, MoSJE | G.S.R. 423(E), April 2016 | Prescribes mandatory relief amounts (Annexure I), 60-day investigation deadlines, and protection mandates. |
| `SRC-GOV-04` | **National Helpline Against Atrocities (NHAA - 14566) Launch Notification** — Press Information Bureau (PIB), MoSJE | Dec 13, 2021 | Establishes 24/7 toll-free helpline `14566` / `1800-202-1989` across India in English, Hindi, and regional languages. |
| `SRC-GOV-05` | **SAMBAL Scheme Guidelines** — Department of Social Justice & Empowerment, MoSJE | 2022–2026 Guidelines | Framework for Strengthening Access to Grievance Redressal and monitoring PCR/PoA implementation. |
| `SRC-GOV-06` | **National Tele Mental Health Programme (Tele-MANAS) Notification** — MoHFW / NIMHANS | Oct 10, 2022 (Verified Aug 2026) | 24/7 nationwide mental health service `14416` / `1800-891-4416` across 53 cells in all 36 States/UTs in 20 languages; basis for `TeleManasAdapter`. |
| `SRC-GOV-07` | **The Digital Personal Data Protection Act, 2023 (DPDP Act 2023)** — Ministry of Electronics & IT (MeitY) | Act No. 22 of 2023 | Mandates purpose limitation, explicit consent notice, verifiable parental consent, and data fiduciary audit obligations. |
| `SRC-GOV-08` | **Guidelines for Indian Government Websites (GIGW 3.0)** — National Informatics Centre (NIC) / MeitY | 2023 Standard | Enforces WCAG 2.1 AA accessibility, multi-lingual rendering, cybersecurity conformance, and citizen trust UX. |
| `SRC-GOV-09` | **Witness Protection Scheme, 2018** — Ministry of Home Affairs / Supreme Court of India (*Mahender Chawla v. UOI*) | (2019) 14 SCC 615 | Legal foundation for threat-based witness relocation, identity shielding, and fast-track protection orders via District Committees. |
| `SRC-GOV-10` | **Legal Services Authorities Act, 1987 & NALSA 15100** — Ministry of Law & Justice / NALSA | Act No. 39 of 1987 | Mandates free legal services to SC/ST persons under Section 12(b); National Legal Aid Helpline `15100`. |
| `SRC-GOV-11` | **Emergency Response Support System (ERSS 112)** — Ministry of Home Affairs (MHA) | Unified Pan-India 112 | Unified emergency call response for police, fire, health, and rescue across all 36 States/UTs. |

---

## 2. Clinical & Trauma-Informed Framework Sources

| Source Identifier | Title & Organization | Authors / Publication | Application to Product |
| :--- | :--- | :--- | :--- |
| `SRC-CLN-01` | **Trauma-Informed Care in Behavioral Health Services** — Substance Abuse and Mental Health Services Administration (SAMHSA) | Treatment Improvement Protocol (TIP 57), 2014 | Foundational 6 principles: Safety, Trustworthiness & Transparency, Peer Support, Collaboration, Empowerment, Cultural Humility. |
| `SRC-CLN-02` | **The Columbia-Suicide Severity Rating Scale (C-SSRS)** — Columbia University | Posner et al., 2011 | Informs the safety-critical multi-layer suicidal ideation detection taxonomy, separating passive ideation from imminent intent. |
| `SRC-CLN-03` | **Psychological First Aid (PFA): Field Operations Guide** — National Child Traumatic Stress Network (NCTSN) / WHO | NCTSN & NC-PTSD, 2006 | Guides operator prompt templates: non-intrusive safety inquiry, emotional stabilization, practical assistance matching. |

---

## 3. Speech & Machine Learning Scientific Foundations

| Source Identifier | Title / System | Key Reference | Engineering Application |
| :--- | :--- | :--- | :--- |
| `SRC-ML-01` | **IndicWav2Vec & IndicConformer: Speech Recognition for Indian Languages** — AI4Bharat | Javed et al., Interspeech / NeurIPS 2022-2024 | Benchmark for Indic language ASR and code-switching error tolerance. |
| `SRC-ML-02` | **The Geneva Minimalistic Acoustic Parameter Set (GeMAPS) for Voice Research and Affective Computing** — IEEE TAC | Eyben et al., IEEE TAC, 2016 | Source standard for openSMILE acoustic feature extraction (F0, jitter, shimmer, spectral flux). |
| `SRC-ML-03` | **MuRIL: Multilingual Representations for Indian Languages** — Google Research India | Khanuja et al., arXiv:2103.11152, 2021 | Core multilingual semantic text representation model for Indian languages. |
| `SRC-ML-04` | **Robust Speech Recognition via Large-Scale Weak Supervision (Whisper)** — OpenAI | Radford et al., ICML 2023 | Baseline ASR encoder-decoder architecture; implemented via CTranslate2 `faster-whisper`. |
| `SRC-ML-05` | **WebRTC Voice Activity Detector (VAD)** — Google / WebRTC Project | RFC 7874 / Chromium Source | Sub-second audio segmentation and pause boundary detection. |
