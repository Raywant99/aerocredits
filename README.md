# AeroCredits: B2B Supply Chain Invoice Loan Engine

[![Antigravity SDK](https://img.shields.io/badge/Antigravity_SDK-Autonomous_Multi--Agent-38bdf8)](https://github.com/google-antigravity/antigravity-sdk-python)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-GCS_%26_PubSub-4285F4)](https://cloud.google.com)
[![Regulatory Standard](https://img.shields.io/badge/Compliance-Basel_III_%7C_SOC2-10b981)](#)
[![Python Version](https://img.shields.io/badge/Python-3.14%2B-blue)](#)

**AeroCredits** is an enterprise working capital loan engine and invoice discounting platform. It connects suppliers, Fortune 500 corporate buyers, and institutional financial lenders into a unified real-time dashboard to auto-approve short-term business loans based on verified logistics and ERP invoice records.

Built with the **Google Antigravity SDK** and **Google Cloud integration**, AeroCredits deploys an autonomous multi-agent financial audit team that eliminates financing friction while maintaining stringent risk control through multi-tier compliance checks and **Human-In-The-Loop (HITL)** approval gates for high-value loans.

---

## 🏛️ Platform Architecture & Stakeholder Ecosystem

```
+------------------------------------------------------------------------------------------------+
|                                    AEROCREDITS UNIFIED PLATFORM                                 |
+------------------------------+----------------------------------+------------------------------+
|     🏢 SUPPLIER PORTAL       |    🏛️ CORPORATE BUYER ERP        |   🏦 FINANCIAL LENDER DESK   |
| - Instant Invoice Ingestion  | - Authorized Purchase Orders     | - Institutional Liquidity    |
| - 85-90% Advance Liquidity   | - Goods Receipt Notes (GRN)      | - $35M+ Aggregated Pools     |
| - Payout in < 180 seconds    | - Proof of Delivery (POD) Signoff| - High-Value HITL Gate       |
+------------------------------+----------------------------------+------------------------------+
                                                │
                                                ▼
+────────────────────────────────────────────────────────────────────────────────────────────────+
|              GOOGLE CLOUD STORAGE VAULT (`gs://aerocredits-vault-inbound`)                     |
|                   Encrypted Document Parsing & SHA-256 Checksum Index                          |
+────────────────────────────────────────────────────────────────────────────────────────────────+
                                                │
                                                ▼
+────────────────────────────────────────────────────────────────────────────────────────────────+
|                 ANTIGRAVITY AUTONOMOUS MULTI-AGENT FINANCIAL AUDIT TEAM                        |
|                                                                                                |
|   [1. Ingestion Agent] ──▶ [2. 3-Way Match] ──▶ [3. Compliance] ──▶ [4. Underwriting]         |
|   Cloud Vault & OCR       PO vs Inv vs GRN       Tax, KYC, AML        LTV & Dynamic APR        |
|                                                                             │                  |
|                                                                             ▼                  |
|                                                                 [5. Gatekeeper Agent]          |
|                                                                             │                  |
|                                              ┌──────────────────────────────┴───────────────┐  |
|                                              ▼                                              ▼  |
|                                      Tier-1: < $100k                              Tier-2: >= $100k     |
|                                    ⚡ Auto-Approval                                ⚠️ HITL Gate        |
|                              Disbursed to Bank Account                   Escalated for Officer Signoff |
+────────────────────────────────────────────────────────────────────────────────────────────────+
                                                │
                                                ▼
+────────────────────────────────────────────────────────────────────────────────────────────────+
|                     IMMUTABLE REGULATORY AUDIT LEDGER (SHA-256 CHAINED)                        |
|        Block Height #0 (Genesis) ──▶ Block #1 ──▶ Block #2 ──▶ ... ──▶ Block #N                |
|               Exportable Compliance Package for Regulators (Basel III & SOC2)                  |
+────────────────────────────────────────────────────────────────────────────────────────────────+
```

---

## 🤖 The Autonomous Multi-Agent Team

1. **Document Ingestion Agent (`AeroCredits-IngestionAgent-01`)**:
   - Ingests raw invoices from Google Cloud Storage (`gs://aerocredits-vault-inbound/`).
   - Extracts structured line items, quantities, currency, net payment terms, and calculates taxes.
   - Computes SHA-256 content hashes to guarantee file integrity.

2. **3-Way Reconciliation Agent (`AeroCredits-ReconcileAgent-02`)**:
   - Performs automated 3-way reconciliation:
     $$\text{Purchase Order (ERP)} \iff \text{Invoiced Line Items} \iff \text{Carrier Goods Receipt (GRN)}$$
   - Matches SKUs, verifies delivered quantities vs. billed quantities (flags shortfalls/overbilling), and compares PO authorized pricing vs invoiced unit prices.
   - Generates a **3-Way Reconciliation Score (0-100%)**.

3. **Multi-Tier Compliance Agent (`AeroCredits-ComplianceAgent-03`)**:
   - **Tier 1**: Real-time Tax ID & GST/VAT verification (active taxpayer status).
   - **Tier 2**: Sanctions & PEP screening against OFAC, EU, and UN watchlists.
   - **Tier 3**: Graph-based anti-fraud and circular trading detection (detects fabricated reciprocal transactions).
   - **Tier 4**: Credit facility ceiling checks against the anchor buyer's authorized credit limit.

4. **Quantitative Risk & Underwriting Agent (`AeroCredits-UnderwriteAgent-04`)**:
   - Evaluates buyer credit ratings (e.g. Boeing: AAA / 980; Nvidia: AAA / 992; Pfizer: AA+ / 945).
   - Determines the **Loan-to-Value (LTV)** advance rate (80% to 90%).
   - Prices the **Annualized Discount Rate (APR)**:
     $$\text{APR} = \text{Benchmark SOFR (4.75\%)} + \text{Buyer Risk Spread} + \text{Tenure Margin}$$
   - Calculates discount fees and net cash disbursement.

5. **Governance & Approval Gatekeeper Agent (`AeroCredits-Gatekeeper-05`)**:
   - **Tier-1 Auto-Approval Policy**: Loans $< \$100,000$, with 3-way match score $\ge 95\%$ and clean compliance are **auto-approved and disbursed instantly** from institutional liquidity pools.
   - **Tier-2 Human-In-The-Loop Gate (HITL)**: Loans $\ge \$100,000$, or invoices with delivery variances / compliance flags, are **automatically paused and escalated** to the credit officer review desk with highlighted evidence.
   - Appends an immutable cryptographic block to the audit ledger.

---

## 🔒 Cryptographic Audit Ledger & Compliance

Every action, agent thought, reconciliation score, and human officer decision is recorded in a tamper-evident blockchain-style ledger:
- **Block Height**: Sequential indexing starting from Genesis Block #0.
- **Hash Pointer**: Each block contains `previous_hash` pointing to the previous block's SHA-256 hash:
  $$\text{Block Hash} = \text{SHA256}(\text{Height} \parallel \text{Timestamp} \parallel \text{Agent} \parallel \text{Action} \parallel \text{Payload} \parallel \text{PrevHash})$$
- **Verification**: The `/api/audit/verify` endpoint verifies the integrity of every link in the chain in real-time.
- **Regulatory Export**: Fully compliant with Basel III and SOC2 reporting standards.

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+
- Modern Web Browser (Chrome, Edge, Firefox)

### 2. Launch the Application
Run the launcher script:
```powershell
python run.py
```
Or start via uvicorn / flask:
```powershell
python backend/app.py
```

Open your browser to:
**http://127.0.0.1:5055**

---

## 🧪 Testing Enterprise Scenarios

AeroCredits comes pre-loaded with four enterprise test scenarios accessible directly in the UI modal or via API:

1. **Aerospace Turbine Blades ($84,672.00)**:
   - Supplier: AeroTech Precision ➔ Buyer: Boeing Commercial
   - Match: 100% SKU parity, 40/40 units delivered via FedEx Freight.
   - Decision: **Tier-1 Auto-Approved & Disbursed** in 180ms.

2. **Semiconductor Silicon Wafers ($49,896.00)**:
   - Supplier: NanoSilicon ➔ Buyer: Nvidia Corp
   - Match: 100% SKU parity, 120/120 units delivered via Maersk Logistics.
   - Decision: **Tier-1 Auto-Approved & Disbursed**.

3. **Heavy Titanium Containment Rings ($264,600.00)**:
   - Supplier: AeroTech Precision ➔ Buyer: Boeing Everett Facility
   - Value: $264,600 exceeds the $100,000 HITL threshold.
   - Decision: **Tier-2 Escalated to Human-In-The-Loop Approval Gate**.
   - Officer can review multi-agent audit notes and click **"Authorize & Disburse"**.

4. **Pharma Cold-Chain Delivery Shortfall ($66,960.00)**:
   - Supplier: BioVax ➔ Buyer: Pfizer Biopharma
   - Discrepancy: Invoiced for 500 vials, carrier waybill notes receiving inspector sign-off for only 450 vials (50 shortfall).
   - Decision: **3-Way Match score drops to 70% ➔ Escalated to Human Officer**.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | System status, Antigravity SDK engine, and GCP parameters |
| `/api/metrics` | GET | Real-time aggregate volume, auto-approval rate, and lender pools |
| `/api/invoices` | GET | List all ingested invoices and line-item details |
| `/api/invoices/ingest` | POST | Ingest document to GCS vault and trigger multi-agent audit |
| `/api/loans` | GET | Retrieve loan requests, underwriting, and approval status |
| `/api/hitl/pending` | GET | Fetch loans currently in the Human-In-The-Loop review queue |
| `/api/hitl/decision` | POST | Submit officer sign-off (`APPROVED` / `REJECTED`) with notes |
| `/api/audit/chain` | GET | Retrieve immutable SHA-256 chained audit blocks |
| `/api/audit/verify` | GET | Verify cryptographic integrity across all blocks |
| `/api/audit/export` | GET | Download complete regulatory compliance bundle |

---

## 📄 License
Enterprise MIT License &copy; 2026 AeroCredits. Powered by Antigravity SDK & Google Cloud.
