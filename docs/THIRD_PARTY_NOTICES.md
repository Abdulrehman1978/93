# Third-Party Notices & Open Source Attributions

> **Document ID:** THIRD-PARTY-NOTICES-V2  
> **Last Verified:** October 2026

---

## 1. Core Open-Source Dependencies & Licenses

| Component / Package | Upstream Project / Author | License | Usage in Architecture | Modifications / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI** | Sebastián Ramírez (tiangolo) | MIT | Modular monolith backend REST & WebSocket API gateway | Unmodified; standard dependency |
| **Pydantic (v2)** | Samuel Colvin & Pydantic Contributors | MIT | Strict data contracts, schema validation, and OpenAPI generation | Unmodified; typed models |
| **faster-whisper** | SYSTRAN & OpenAI | MIT | High-performance local speech-to-text inference with CTranslate2 | Wrapped in `SpeechToTextProvider` abstraction |
| **librosa** | Brian McFee et al. | ISC (BSD compatible) | DSP audio feature extraction (F0 tracking via pyin, RMS energy, spectral flux) | Used for CPU-based acoustic analysis |
| **webrtcvad** | John Wiseman / Google | MIT | Sub-second voice activity detection and audio pause segmentation | Integrated into streaming speech processor |
| **SQLAlchemy (v2)** | Michael Bayer | MIT | Asynchronous relational ORM & database query builder | Parameterized queries with strict typing |
| **Next.js (v14/v15)** | Vercel, Inc. | MIT | React server/client framework for Citizen PWA and Operator Copilot | App Router, Server Components |
| **Tailwind CSS** | Tailwind Labs, Inc. | MIT | Utility-first CSS styling engine configured for Civic Calm tokens | Custom theme extensions in `tailwind.config.ts` |
| **Lucide Icons** | Lucide Contributors | ISC | Accessible, lightweight SVG icon set for civic and operational UI | Rendered with accessible labels |
| **Axe-core** | Deque Systems, Inc. | MPL-2.0 | Automated accessibility auditing engine for WCAG 2.1 AA verification | Integrated into CI and test runner |
| **PyTest** | Holger Krekel and contributors | MIT | Automated Python testing framework for unit and integration tests | Standard test runner |
| **Playwright** | Microsoft Corporation | Apache-2.0 | End-to-end browser automation and visual regression testing | Used for E2E testing |

---

## 2. Intellectual Property & Attribution Notice
- **SAMBAL Intelligence & Response Layer** is an independent, original technical implementation developed for the Ministry of Social Justice and Empowerment's Smart India Hackathon (SIH26093) initiative.
- All references to statutory laws (PCR Act 1955, PoA Act 1989, DPDP Act 2023) and government schemes (NHAA 14566, SAMBAL, Tele-MANAS, NALSA) are public domain statutory and operational references.
- No copyrighted proprietary code or confidential datasets from government or private entities have been incorporated.
