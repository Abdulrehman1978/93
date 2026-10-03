# SAMBAL Intelligence Layer — Comprehensive Cost Engineering Model

> **Document ID:** COST-MODEL-V2  
> **Topic:** Operational Cost Breakdown Across Deployment Tiers  
> **Currency:** Indian Rupee (INR ₹) & USD ($) reference  
> **Methodology:** Unit economic modeling of ASR, LLM tokens, compute, storage, telephony, and SMS gateways.

---

## 1. Unit Economics & Component Cost Drivers

| Service Component | Open-Source / Local Self-Hosted Path | Commercial SaaS / Cloud API Path | Government / Subsidized Path | Recommended Production Baseline |
| :--- | :--- | :--- | :--- | :--- |
| **Speech-to-Text (ASR)** | **₹0.00 / min** (Self-hosted `faster-whisper-turbo` on CPU/GPU server) | ₹0.50 / min ($0.006/min OpenAI / Google Cloud STT) | ₹0.00 (Bhashini National Mission API for Gov) | **Self-hosted local ASR + Bhashini Gateway** |
| **Translation** | **₹0.00** (Local IndicTrans2 ONNX model) | ₹0.0016 / 1000 chars (Google Cloud Translation) | ₹0.00 (Bhashini Translation API) | **Local IndicTrans2 + Bhashini** |
| **LLM Reasoning & Extraction** | **₹0.00** (Local Llama-3-8B-Instruct on GPU) | ₹0.04 / 1k input tokens, ₹0.12 / 1k output tokens (Gemini 1.5 Flash) | NIC Cloud / MeghRaj Hosted LLM | **Hybrid: Gemini 1.5 Flash for primary; local fallback** |
| **DSP Acoustic Features** | **₹0.00** (Native Python `librosa` / `openSMILE` / WebRTC VAD on CPU) | N/A | N/A | **Self-hosted native CPU DSP** |
| **Relational Database** | Managed PostgreSQL on Linux VM / Cloud SQL (₹2,500 – ₹18,000 / month) | AWS Aurora PostgreSQL (₹12,000+ / month) | NIC MeghRaj Cloud PostgreSQL (Subsidized) | **Standard PostgreSQL 16+** |
| **Object Storage (Attachments/Logs)** | MinIO S3-Compatible on VM storage (₹1.50 / GB / month) | AWS S3 Standard (₹1.90 / GB / month) | NIC MeghRaj Object Store | **MinIO / S3 Standard with 90-day auto-purge** |
| **Inbound Telephony (PSTN / PRI)** | ₹0.35 / min (Bulk enterprise SIP trunking in India) | ₹0.85 / min (Twilio / Exotel commercial pricing) | BSNL / MTNL Government PRI Lines (Budgeted) | **Existing 14566 BSNL/MTNL PRI infrastructure** |
| **SMS Notifications (Docket/Referral)** | ₹0.12 / SMS (Govt DLT SMS gateway bulk rate) | ₹0.25 / SMS (Commercial Twilio/Msg91) | NIC / CDAC e-Gov SMS Gateway (₹0.08 / SMS) | **NIC / CDAC SMS Gateway** |

---

## 2. Multi-Tier Scaling Cost Projections

### Tier 1: Hackathon & Live Demo Environment
- **Scope:** 5 concurrent interactive sessions; 500 test calls/transcripts; synthetic scenario evaluation.
- **Infrastructure:** 1x 4-Core CPU, 16GB RAM Cloud VM (e.g., Hetzner / DigitalOcean / AWS t3.xlarge).
- **Compute Cost:** ~₹3,500 / month ($42/mo).
- **AI Token Cost:** ~₹800 / month (Gemini Flash development tier).
- **Storage & Networking:** ₹400 / month.
- **Total Monthly Cost:** **₹4,700 / month (~$56 USD)**.

### Tier 2: Single District Pilot
- **Scope:** 1 high-atrocity district (e.g., 60 calls/day, average duration 6 minutes = 360 call minutes/day).
- **Monthly Volume:** ~10,800 audio minutes; 1,800 case dockets.
- **Compute (2x Dedicated App/AI VMs):** ₹12,000 / month.
- **AI Processing (Hybrid Local ASR + Gemini Flash):** ₹3,800 / month.
- **PostgreSQL Database & Daily Backups:** ₹3,500 / month.
- **SMS Gateway Notifications (1,800 * 3 updates):** ₹650 / month.
- **Total Monthly Cost:** **₹19,950 / month (~$240 USD)**.

### Tier 3: State-Wide Deployment (e.g., Maharashtra or Uttar Pradesh)
- **Scope:** 35 districts; ~1,500 calls/day = 9,000 audio minutes/day.
- **Monthly Volume:** ~270,000 minutes; 45,000 dockets.
- **Compute (Cluster of 4x GPU-accelerated nodes for ASR + 2x App nodes):** ₹95,000 / month.
- **Managed High-Availability PostgreSQL (Cloud SQL / Aurora):** ₹28,000 / month.
- **AI Token Reserve (Gemini / Bhashini):** ₹22,000 / month.
- **SMS / Telephony Trunking Management:** ₹18,000 / month.
- **Total Monthly Cost:** **₹1,63,000 / month (~$1,960 USD)**.
- **Cost Per Complainant Served:** **₹3.62 per case docket**.

### Tier 4: National Scale (All 36 States & UTs)
- **Scope:** Pan-India 14566 operations; ~15,000 calls/day; 90,000 audio minutes/day.
- **Monthly Volume:** 2.7 Million audio minutes; 450,000 cases handled annually.
- **Hosting Environment:** National Informatics Centre (NIC) MeghRaj Cloud or dedicated Ministry Data Centre.
- **Capital Hardware Allocation (Kubernetes Node Pool with 8x NVIDIA L4 GPUs):** ~₹6,50,000 / month equivalent.
- **Enterprise DB & Storage Cluster:** ₹1,20,000 / month.
- **Network Bandwidth & Redundancy:** ₹80,000 / month.
- **Total Monthly Cost:** **~₹8,50,000 / month (~$10,200 USD)**.
- **Cost Per Complainant Served:** **~₹1.88 per case**.

---

## 3. Cost-Optimization Architecture Principles
1. **Zero-Per-Minute Commercial ASR Trap:** Never lock public helpline economics into commercial ASR APIs ($0.006/min = $16,200/mo at national scale). Self-hosting `faster-whisper` cuts variable costs to zero marginal compute.
2. **Ephemeral Audio Disposal:** Purging raw audio immediately after session processing prevents runaway petabyte storage bills and minimizes DPDP compliance liability.
3. **Deterministic Safety Rule Pre-Filtering:** By executing Layer 1 regex safety rules before LLM token generation, over 40% of standard operational triage decisions avoid external API calls entirely.
