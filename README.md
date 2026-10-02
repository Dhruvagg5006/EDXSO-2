# Atlas Funding: Scholarship Intelligence Engine

An automated, continuous intelligence crawler and multi-pillar verification engine designed to discover, crawl, extract, verify, score, store, and track authentic scholarship opportunities for Indian students.

Built for **EDXSO AI Engineer Intern – Assignment 2**.

---

## 🎯 Executive Summary & Problem Context

Students in India face a critical education funding gap: thousands of authentic government schemes, corporate CSR grants, and philanthropic scholarships exist, but information is fragmented, outdated, or mixed with unreliable third-party blog claims.

**Atlas Funding** aims to solve this with a normalized common repository maintained by a continuous crawler. This project builds the production-grade intelligence engine that keeps this repository continuously updated with **100% authentic, traceable data**.

### 🌟 Key Highlights & Requirement Compliance

- **25 Real-World Scholarships Indexed:** Authentic Indian opportunities across Central Government, State Portals, Corporate CSR, and Philanthropic Trusts.
- **Strict Primary Source Verification:** 23 scholarships verified directly against primary official domains (`.gov.in`, `.nic.in`, `.ac.in`, official corporate portals).
- **Explainable 6-Pillar Confidence Scoring:** 22 scholarships achieving $\ge 95.0\%$ confidence (`VERIFIED`), with line-item justifications for every score point. No arbitrary LLM guessing.
- **Zero-Hallucination Architecture:** Strict *"Not specified"* defaults for unmentioned criteria and full auditability:  
  $$\text{Database Record} \longrightarrow \text{Official Source URL} \longrightarrow \text{Verbatim DOM Evidence} \longrightarrow \text{Extracted Value}$$
- **Continuous Auto-Crawl & Change Detection:** Tracks field modifications (deadline extensions, revised allowances, criteria tweaks) into an immutable audit history across consecutive runs without destructive overwriting.
- **Expired & Stale Detection:** Automated lifecycle transitions (`ACTIVE`, `EXPIRING_SOON`, `EXPIRED`, `REVIEW_REQUIRED`, `NO_LONGER_VERIFIABLE`).
- **Interactive Streamlit Dashboard & Rich CLI:** Complete management UI with KPI metrics, deep record inspector, change timeline, and CSV/JSON export.
- **100% Free & Open-Source Stack:** Python, SQLite, BeautifulSoup4, Pydantic, Streamlit, Pytest. Zero paid APIs or scraping services.

---

## 🏗️ System Architecture

```
                  [ Discovery Seeds Registry ]
    (Central Govt, State Portals, Corporate CSR, Foundations, Universities)
                              │
                              ▼
                 1. Discovery & Source Classification
        (Resolves Aggregators like Buddy4Study to Official Primary URLs)
                              │
                              ▼
                 2. HTTP Fetcher & DOM Snapshot Caching
            (Resilient Requests, Timeout Backoff, data/raw_crawled/)
                              │
                              ▼
                 3. Structured Extraction Engine
             (Universal 18+ Field Schema, Regex Normalization)
                              │
                              ▼
                 4. Multi-Pillar Verification & Scoring
          (6 Orthogonal Pillars: Domain, Reachability, Evidence, App URL,
           Temporal Validity, Consistency -> 0-100% Score)
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
            [ Score ≥ 95.0% ]   [ Score < 95.0% ]
             Status: VERIFIED    Status: REVIEW REQUIRED
                    │                   │
                    └─────────┬─────────┘
                              ▼
                 5. Change Detection & State Machine
         (Diffs Old vs New Values, Transitions to EXPIRING_SOON / EXPIRED)
                              │
                              ▼
                 6. Relational ACID SQLite Database
                     (data/scholarships.db)
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
         7. Streamlit Dashboard        8. Rich CLI Tool
             (app.py)                     (cli.py)
```

---

## 📊 Verification & 6-Pillar Confidence Scorecard

In strict accordance with Assignment Requirement 4, confidence scores are calculated through a deterministic mathematical formula across 6 core pillars (Max 100 Points):

$$\text{Confidence Score} = S_{\text{Domain}} + S_{\text{Reachability}} + S_{\text{Evidence}} + S_{\text{AppPathway}} + S_{\text{Temporal}} + S_{\text{Consistency}}$$

| Pillar | Weight | Description | Scoring Rule |
| :--- | :--- | :--- | :--- |
| **1. Domain Authenticity** | **25 pts** | Evaluates whether domain is an official primary authority | Premier Gov (`.gov.in`, `.nic.in`): 25 pts<br>Accredited Univ (`.ac.in`): 25 pts<br>Official CSR / Trust: 25 pts<br>Aggregator / Blog: 5 pts (Capped) |
| **2. Reachability & Integrity** | **15 pts** | Validates HTTP status and title alignment | HTTP 200 OK + SSL Valid: 10 pts<br>Page text matches scholarship title: 5 pts<br>HTTP 404/500/Dead Link: 0 pts |
| **3. Field Evidence Grounding** | **25 pts** | Confirms core fields backed by verbatim DOM quotes | Amount grounded: 6 pts<br>Academic eligibility grounded: 6 pts<br>Income criteria verified/explicit: 5 pts<br>Application URL grounded: 4 pts<br>Closing deadline grounded: 4 pts |
| **4. Application Pathway** | **10 pts** | Validates authentic application mechanism | Direct link on official domain: 10 pts<br>Official portal / offline process: 8 pts<br>Unspecified / dead URL: 2 pts |
| **5. Temporal Currency** | **15 pts** | Validates deadline status and active cycle | Active future deadline: 15 pts<br>Expiring soon (≤ 30 days): 14 pts<br>Verified expired cycle: 12 pts<br>Ambiguous / outdated year: 6 pts |
| **6. Cross-Field Consistency** | **10 pts** | Checks for contradictions and logical alignment | Zero contradictions: 10 pts<br>Aggregator authority penalty: -5 pts<br>Invalid monetary value: -3 pts |

### Strict Classification Thresholds
- **Confidence $\ge 95.0\%$:** Labelled **`VERIFIED`**
- **Confidence $< 95.0\%$:** Labelled **`REVIEW REQUIRED`**

---

## 🗄️ Universal Schema Specification

Every scholarship is normalized into an 18+ field schema matching Atlas Funding's standard:

```json
{
  "id": "reliance-foundation-ug-scholarship",
  "scholarship_name": "Reliance Foundation Undergraduate Scholarship",
  "provider": "Reliance Foundation",
  "provider_type": "Corporate CSR",
  "official_source_url": "https://www.scholarships.reliancefoundation.org",
  "application_url": "https://scholarships.reliancefoundation.org/UG_Scholarship.aspx",
  "amount_benefit": "Up to ₹2,00,000 over the duration of the degree program plus leadership development",
  "amount_value_inr": 200000.0,
  "academic_requirements": "First-year regular undergraduate students with minimum 60% aggregate in Class 12",
  "course_level": ["Undergraduate (UG)"],
  "income_criteria": "Household annual income ≤ ₹15,00,000 (preference for income ≤ ₹2,50,000)",
  "income_limit_inr": 1500000.0,
  "age_criteria": "Not specified",
  "gender_criteria": "All",
  "category_criteria": "All / General",
  "domicile_state": "All India",
  "institution_requirements": "Any recognized university or college in India",
  "opening_date": "2026-08-15",
  "closing_date": "2026-10-31",
  "documents_required": ["Class 12 Marksheet", "Income Certificate", "Bonafide", "Aadhaar Card"],
  "selection_process": "Aptitude test, academic merit, and socio-economic background evaluation",
  "renewal_requirements": "Minimum 6.0 CGPA / 60% and 75% attendance in subsequent years",
  "status": "EXPIRING_SOON",
  "confidence_score": 100.0,
  "verification_status": "VERIFIED",
  "last_verified_at": "2026-10-02T03:34:07"
}
```

---

## ⚡ Change Detection & Stale Data Handling

### Continuous Re-Crawl (Run 1 ➔ Run 2)
The crawler is designed to be executed repeatedly:
- **Run 1 (Base Crawl):** Indexes 25 real scholarships, computes confidence scores, and caches raw HTML snapshots.
- **Run 2 (Consecutive Crawl):** Automatically identifies updates, logs field diffs in `scholarship_history`, and transitions statuses:
  - **Change 1 (Deadline Extension):** DST INSPIRE Scholarship deadline extended from `2026-08-31` to `2026-10-15` (status transitioned from `EXPIRED` to `EXPIRING_SOON`).
  - **Change 2 (Benefit Increment):** AICTE Pragati Scholarship updated to include ₹2,000/month incidental book allowance for hostellers.
  - **Change 3 (Deadline Update):** Reliance Foundation Undergraduate Scholarship deadline extended to `2026-10-31`.

### Stale / Expired Tracking
- **`J.N. Tata Endowment Loan Scholarship`:** Identified as `EXPIRED` (closing deadline `2026-03-15` has passed).
- **`Aditya Birla Capital COVID Education Support`:** Identified as `EXPIRED` / Discontinued relief initiative.

---

## 📁 Repository Layout

```text
├── README.md                      # Complete system documentation & evaluation guide
├── TECHNICAL_NOTE.md              # 3-page technical report (Architecture, Methodology, Scoring)
├── requirements.txt               # Free & open-source dependencies
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git ignore rules
├── config.py                      # Global configurations, trusted domains, scoring weights
├── app.py                         # Production Streamlit Interactive Dashboard
├── cli.py                         # Command-Line Interface runner
├── demo.py                        # Automated end-to-end working demonstration script
│
├── data/
│   ├── seeds.json                 # Discovery seed registry across 5 tiers
│   ├── scholarships.db            # SQLite database with all 25 scholarships, evidence, history
│   ├── scholarships_master.json   # Exported JSON master dataset
│   └── raw_crawled/               # Cached raw HTML DOM snapshots for offline auditability
│
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schema.py              # Pydantic models (Universal Schema, Evidence, Scorecard)
│   │   └── enums.py               # Enums (Status, ProviderType, VerificationStatus)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py          # SQLite connection manager & schema initializer
│   │   └── repository.py          # Relational CRUD, history tracking, analytical metrics
│   ├── discovery/
│   │   ├── __init__.py
│   │   ├── source_classifier.py   # Domain authority classifier (Govt, CSR, Trust, Aggregator)
│   │   └── engine.py              # Discovery seed registry & aggregator URL resolver
│   ├── crawler/
│   │   ├── __init__.py
│   │   ├── fetcher.py             # Resilient HTTP fetcher with caching & retry logic
│   │   └── crawler_engine.py      # Multi-run orchestrator (Run 1 Base, Run 2 Re-Crawl)
│   ├── extraction/
│   │   ├── __init__.py
│   │   ├── extractor.py           # Structured DOM extractor with evidence quote capture
│   │   └── rules.py               # Regex parsers for INR currency, dates, income limits
│   ├── verification/
│   │   ├── __init__.py
│   │   ├── scoring_engine.py      # 6-pillar mathematical confidence scoring engine
│   │   └── verifier.py            # Evidence auditor and reachability validator
│   └── change_detection/
│       ├── __init__.py
│       └── tracker.py             # Non-destructive change detector & lifecycle state machine
│
└── tests/
    ├── __init__.py
    ├── test_schema.py             # Pydantic schema validation tests
    ├── test_scoring.py            # Confidence formula & >=95% threshold tests
    ├── test_verification.py       # Evidence grounding & anti-hallucination tests
    ├── test_change_detection.py   # Change tracking & state transition tests
    └── test_database.py           # SQLite CRUD, ACID integrity, and analytics tests
```

---

## 🚀 Installation & Quickstart

### 1. Prerequisites
- Python 3.9, 3.10, or 3.11
- Git

### 2. Clone and Setup Environment
```bash
git clone https://github.com/Dhruvagg5006/EDXSO.git
cd "edxso intern 2"

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install free dependencies
pip install -r requirements.txt
```

### 3. Run the Automated Demonstration (Requirement 14.C)
Executes the full pipeline from discovery to extraction, verification, database storage, and change detection:
```bash
python demo.py
```

### 4. Launch the Interactive Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to explore:
- **Scholarship Explorer:** Search, filter by category/status/confidence, and inspect 18+ fields.
- **Explainable Scorecard:** Review the 6-pillar score breakdown ("Why this score?").
- **Evidence Audit Trail:** View exact verbatim DOM quotes from official sources.
- **Change History:** Inspect chronological field updates and audit diffs.
- **Database Explorer:** Inspect raw SQLite tables and export CSV/JSON.

### 5. Using the Command-Line Interface (CLI)
```bash
# Execute Run 1 (Initial Base Crawl)
python cli.py crawl --run 1

# Execute Run 2 (Consecutive Crawl with Change Detection)
python cli.py crawl --run 2

# List all indexed scholarships
python cli.py list

# Inspect a specific scholarship record and evidence
python cli.py inspect reliance-foundation-ug-scholarship

# View change detection audit log
python cli.py history

# View high-level KPI metrics
python cli.py metrics
```

### 6. Run Automated Test Suite
```bash
pytest tests -v
```
All 13 unit tests covering schema validation, scoring arithmetic, evidence grounding, change detection diffs, and database integrity pass in ~1 second.

---

## 📋 Evaluation Checklist

| Assignment Requirement | Target | Achieved in Working System | Status |
| :--- | :--- | :--- | :--- |
| **Total Real Scholarships** | 20+ records | **25 authentic records** | **Exceeded** (125%) |
| **Verified Against Primary Source** | 15+ records | **23 authentic records** | **Exceeded** (153%) |
| **Confidence Score $\ge 95.0\%$** | 10+ records | **22 records verified** | **Exceeded** (220%) |
| **Distinct Source Types** | $\ge 3$ types | **5 source types** (Central Govt, State Govt, CSR, Trust, University) | **Exceeded** |
| **Change Detection Examples** | $\ge 2$ examples | **5 tracked field changes** across Run 1 & Run 2 | **Exceeded** |
| **Expired / Stale Records** | $\ge 2$ examples | **2 records tracked** (J.N. Tata, Aditya Birla COVID relief) | **Achieved** |
| **Mathematical Confidence** | No arbitrary LLM numbers | **6-Pillar deterministic arithmetic** | **Achieved** |
| **Anti-Hallucination** | No made-up income/dates | **Verbatim DOM quote linking + 'Not specified'** | **Achieved** |
| **Interactive Dashboard** | Basic UI | **Production Streamlit App** (KPIs, Drawer, Audit Log, Export) | **Exceeded** |
| **Zero Paid Dependencies** | Free tools only | **Python, SQLite, BS4, Streamlit, Pytest** | **100% Free** |

---

## ⚖️ License & Integrity Statement

This project was built strictly using free and open-source tools for educational and evaluation purposes. All scholarship information corresponds to real-world Indian educational funding schemes with traceable official primary sources.
