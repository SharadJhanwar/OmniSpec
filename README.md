# ⚡ OmniSpec AI — Industrial Product Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Architecture-LangGraph%209--Agent%20Swarm-cyan?style=for-the-badge&logo=diagramsdotnet" alt="Architecture" />
  <img src="https://img.shields.io/badge/Delivery%20Format-252%20Columns%20(100%25%20Verified)-emerald?style=for-the-badge" alt="252 Columns" />
  <img src="https://img.shields.io/badge/Engine%20Speed-278.6%20SKUs%2Fsec-blue?style=for-the-badge" alt="Speed" />
  <img src="https://img.shields.io/badge/Ground%20Truth-100%25%20Match-success?style=for-the-badge" alt="Accuracy" />
  <img src="https://img.shields.io/badge/Frontend-Vite%20%2B%20React%20%2B%20TailwindCSS-purple?style=for-the-badge&logo=react" alt="React" />
</p>

> **Tagline:** *"From Cryptic Raw Part Rows to 252-Column Commerce-Ready Master Truth."*  
> **Challenge:** Transforming messy, abbreviated industrial distributor feeds (`"3/8 CPLG BRS 150#"`, `"-- Unbranded --"`, missing dimensions) into standardized, search-ready e-commerce catalog master records across all 252 delivery columns with zero hallucinations.

---

## 🏗️ System Architecture & 9-Agent DAG Swarm

OmniSpec AI uses a **hybrid neuro-symbolic multi-agent architecture** orchestrated via **LangGraph**. A high-speed relational knowledge base in **DuckDB** and C++ fuzzy matching via **RapidFuzz** handle deterministic lookups in sub-milliseconds, while an **OpenAI GPT-4o-mini** layer provides intelligent entity disambiguation, rich marketing copywriting, and deep reasoning.

```
                                      [ Raw Messy Supplier Feed ]
                                (MPN, Part_Desc, Dist_Code, Placeholders)
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ Agent 1: Ingestion & De-Noising       │  <── Strips placeholders & parses vendor codes
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ Agent 2: Brand & Entity Resolution   │  <── UniCat 27K DuckDB + RapidFuzz (®, ™)
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ Agent 3: Taxonomy & UNSPSC Classifier│  <── 4-Tier Classpath & 8-Digit UNSPSC
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ Agent 4: Spec, Dim & UOM Extractor   │  <── 63 Exact Fractions & Master UOM Spacing
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ Agent 5: Autonomous OEM Sourcing RAG │  <── Official OEM Whitelist (Banned Portals Filter)
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ Agent 6: Constrained LOV Mapper      │  <── 150-Col EAV (Dishwashers/Fittings/Faucets)
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ Agent 7: Multi-Channel Copy Builder  │  <── Invoice <=40, Mobile 60-80, Short & Long Desc
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ Agent 8: Digital Asset Synthesizer   │  <── <Brand>_<MPN>.jpg & Specification_Sheet.pdf
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                ┌──────────────────────────────────────┐
                                │ Agent 9: Quality Audit & HITL Gate   │  <── 12 Integrity Rules & Provenance Tracer
                                └──────────────────┬───────────────────┘
                                                   │
                                                   ▼
                                [ 252-Column Commerce-Ready Master Truth ]
```

---

## 🤖 Micro-Agent Roles & Capabilities

| Agent | Name | Primary Responsibilities |
| :--- | :--- | :--- |
| **Agent 1** | **Ingestion & De-Noising** | Strips non-data placeholders (`-- Unbranded --`, `-- No DIB Brand --`), unescapes HTML entities, isolates raw dimension tokens, and extracts vendor codes (`APPDE`, `JAMIN`, `BOICA`). |
| **Agent 2** | **UniCat Entity Resolution** | Resolves noisy supplier strings against 27,000+ approved UniCat entities with legal casing (`Inc`, `LLC`, `Co`) and mandatory registered marks (`FRIGIDAIRE®`, `Milwaukee®`, `3M™`, `AZEK®`). |
| **Agent 3** | **Taxonomy & UNSPSC** | Traverses 4-tier category leaf node hierarchies, assigns 8-digit UNSPSC codes, and triggers dynamic LOV schema validation. |
| **Agent 4** | **Spec, Dim & UOM Extractor** | Parses dimension triplets (`L x W x H`), converts decimals to 63 exact fractions (`50.25` $\rightarrow$ `50-1/4 in`), and enforces single-space UOM standards (`24 in`, not `24in`). |
| **Agent 5** | **OEM Sourcing RAG** | Discovers authoritative manufacturer portals, official PDF spec sheets, and regulatory approvals (`ASSE`, `cUL`, `ENERGY STAR`, `ANSI`), while strictly blocking prohibited marketplaces (Amazon, Grainger, etc.). |
| **Agent 6** | **Constrained LOV Mapper** | Maps extracted specs into 50 structured attribute triples (`ATTRIBUTE_LABEL 1..50`, `ATTRIBUTE_VALUE 1..50`, `ATTRIBUTE_UOM 1..50` = 150 columns) adhering strictly to controlled vocabularies. |
| **Agent 7** | **Multi-Channel Copy Builder** | Constructs 6 distinct copy tiers adhering to strict character caps and Unilog formulas: `INVOICE_DESC` ($\le 40$ chars ALL CAPS), `MOBILE_DESC` ($60\text{--}80$ chars), `SHORT_DESC` (PDP Title), `LONG_DESC1`, and `ITEM_FEATURES_1..20`. |
| **Agent 8** | **Digital Asset Synthesizer** | Standardizes primary and alternate images (`<Brand>_<MPN>.jpg`), spec sheets (`<Brand>_<MPN>_Specification_Sheet.pdf`), and document classification links. |
| **Agent 9** | **Quality Audit & HITL Gate** | Executes a 12-point automated integrity suite, calculates weighted confidence scores ($0\text{--}100\%$), and routes low-confidence SKUs to the Human-in-the-Loop Review Studio. |

---

## 📊 Ground Truth Benchmark & Performance Results

### 1. Ground Truth Accuracy (`eval/benchmark_ground_truth.py`)
Tested against the official `Unihack_ Expected Output - Delivery Format.csv`:

```text
=================================================================
OMNISPEC AI: 252-COLUMN GROUND TRUTH BENCHMARK HARNESS
=================================================================
  MANUFACTURER_NAME        : 100.0% Average Similarity
  BRAND_NAME               : 100.0% Average Similarity
  Classpath                : 100.0% Average Similarity
  INVOICE_DESC             : 100.0% Average Similarity (<= 40 chars ALL CAPS)
  MOBILE_DESC              : 100.0% Average Similarity (60-80 chars)
  SHORT_DESC               : 100.0% Average Similarity
  Product Image            : 100.0% Average Similarity (<Brand>_<MPN>.jpg)
  Specification Sheet      : 100.0% Average Similarity (<Brand>_<MPN>_Specification_Sheet.pdf)
  252-Column Delivery Schema: 100% Header Conformant (252 / 252 Columns)
=================================================================
```

### 2. Scale Batch Processing Speed (`eval/run_1000_batch_enrichment.py`)
- **Total Catalog Rows Processed:** 1,000 SKUs
- **Columns Enriched:** Exactly 252 Columns per row
- **Execution Time:** **3.59 seconds**
- **Throughput:** **278.6 SKUs/second**
- **Generated Deliverable:** [`OmniSpec_Enriched_1000_Items_Delivery_252.csv`](./OmniSpec_Enriched_1000_Items_Delivery_252.csv) (1.34 MB)

---

## 💻 Tech Stack

- **AI & Multi-Agent Swarm:** LangGraph, LangChain, OpenAI GPT-4o-mini
- **Database & Search Engine:** DuckDB (In-Memory Relational Engine), RapidFuzz (C++ Levenshtein string matching)
- **Backend API:** FastAPI, Uvicorn, Pydantic v2
- **Frontend Studio:** Vite, React 18, TailwindCSS, Lucide Icons, Glassmorphism UI
- **Languages & Runtime:** Python 3.13+, Node.js v24+

---

## 📁 Project Directory Structure

```text
OmniSpec/
├── backend/
│   └── app/
│       ├── agents/              # 9 Specialized LangGraph Micro-Agents & DAG Graph
│       │   ├── agent_1_ingestion.py
│       │   ├── agent_2_entity_resolution.py
│       │   ├── agent_3_taxonomy.py
│       │   ├── agent_4_spec_uom.py
│       │   ├── agent_5_oem_sourcing.py
│       │   ├── agent_6_lov_mapper.py
│       │   ├── agent_7_copy_builder.py
│       │   ├── agent_8_digital_assets.py
│       │   ├── agent_9_quality_audit.py
│       │   └── graph.py
│       ├── api/                 # FastAPI REST Endpoints (Single, Batch JSON, CSV Stream)
│       │   └── routes.py
│       ├── db/                  # In-Memory DuckDB Knowledge Base Client & Seed Tables
│       │   └── duckdb_client.py
│       ├── schemas/             # Pydantic 252-Column Delivery & State Schemas
│       │   ├── delivery_schema.py
│       │   └── state_schema.py
│       ├── services/            # Normalization, UOM Converter, Fraction & Copy Engines
│       └── main.py              # FastAPI Application Entrypoint
├── frontend/                    # Vite + React Modern Web Studio
│   ├── src/
│   │   ├── components/          # Virtualized 252-Grid, Swarm Visualizer, HITL Modal, Sandbox
│   │   │   ├── AgentSwarmVisualizer.jsx
│   │   │   ├── BatchUploadModal.jsx
│   │   │   ├── DashboardStats.jsx
│   │   │   ├── Grid252.jsx
│   │   │   ├── HITLReviewModal.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── SingleSkuSandbox.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
├── eval/                        # Benchmark & Evaluation Suite
│   ├── benchmark_ground_truth.py
│   ├── run_1000_batch_enrichment.py
│   ├── test_agent.py            # Stage-by-Stage Transformation Tracer
│   └── Result.md                # Comprehensive Verification & Benchmark Report
├── test_agent.py                # Root CLI Transformation Tracer
├── OmniSpec_Enriched_1000_Items_Delivery_252.csv # 252-Col Delivery Export (1,000 SKUs)
├── requirements.txt             # Python Dependencies
└── PLAN.md                      # Implementation & Architectural Roadmap
```

---

## ⚡ Quickstart Guide

### 1. Environment Setup

```powershell
# Clone repository
git clone https://github.com/SharadJhanwar/OmniSpec.git
cd OmniSpec

# Create and activate Python virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```

---

## 🚀 Running the Platform

### A. Start the FastAPI Backend
```powershell
.venv\Scripts\python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
* **Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### B. Start the React Frontend Web Studio
In a second terminal:
```powershell
cd frontend
npm install
npm run dev
```
* **Web Studio URL:** [http://localhost:5173](http://localhost:5173)

---

## 🧪 Testing & Verification Scripts

### 1. Interactive Stage-by-Stage Transformation Tracer
Trace the transformation of any raw SKU across all 9 agents:
```powershell
# Preset 1: Frigidaire Built-In Dishwasher (Large Appliances)
.venv\Scripts\python test_agent.py 1

# Preset 2: Milwaukee Metal Cut-Off Wheel (Abrasives & Cutting Tools)
.venv\Scripts\python test_agent.py 2

# Preset 3: Trex Composite Decking Board (Building Materials)
.venv\Scripts\python test_agent.py 3

# Preset 4: Brass Industrial Pipe Fitting (Plumbing)
.venv\Scripts\python test_agent.py 4
```

### 2. Ground Truth Benchmark Harness
```powershell
.venv\Scripts\python eval/benchmark_ground_truth.py
```

### 3. Run Scale Batch Processing (1,000 SKUs)
```powershell
.venv\Scripts\python eval/run_1000_batch_enrichment.py
```

---

## ✨ Web Studio Features

1. **Live Single-SKU Sandbox**: Type any raw description, select presets, and watch the 9-Agent DAG Swarm execute live with millisecond latencies.
2. **Virtualized 252-Column Data Grid**: Scroll across all attributes, dimensions, and asset links with sticky key identifiers.
3. **HITL Review Studio**: Side-by-side diff comparison, live character counters for `INVOICE_DESC` ($\le 40$) and `MOBILE_DESC` ($60\text{--}80$), and 1-click approvals.
4. **Drag & Drop CSV Ingestion**: Upload any raw 6-column feed and enrich it across 252 columns.
5. **1-Click Export**: Download the delivery-ready CSV deliverable (`OmniSpec_Delivery_Enriched_252.csv`).

---

## 📄 License
MIT License. Built for the UniHack Hackathon Challenge.
