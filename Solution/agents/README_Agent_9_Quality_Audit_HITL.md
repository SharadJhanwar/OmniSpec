# 🛡️ Agent 9: Quality Audit, Lineage Tracer & HITL Orchestrator Agent
### *OmniSpec AI — 12-Rule Integrity Auditor, Evidence-Aware Confidence Scoring & Variable-Level Caching*

---

## 1. Agent Overview & Role

The **Quality Audit, Lineage Tracer & HITL Orchestrator Agent** is the final quality assurance gatekeeper for OmniSpec AI. In enterprise catalog management, unverified AI outputs introduce risk; Agent 9 deterministically tests all 252 generated columns against 12 hard integrity constraints, computes an **Evidence-Aware 5-Pillar Confidence Score** ($0\text{--}100\%$), tracks cell-level cryptographic provenance (DBOM), and enforces strict variable-level caching policies.

### Core Objectives:
1. **12-Point Automated Integrity Suite:** Run comprehensive deterministic audits across character limits, casing, symbols, UOM spaces, and LOV validity.
2. **5-Pillar Evidence-Aware Confidence Engine:** Compute mathematically decomposed confidence from retrieval quality, evidence authority, extraction consistency, cross-source agreement, and deterministic validation.
3. **Variable-Level & Cell-Level Caching Logic:**
   - If an item or attribute is verified in `kb_active_overrides` or Master KB $\rightarrow$ **Confidence = 100.0%**, **`needs_hitl_review = False`** (Bypasses human review).
   - If an item or attribute is newly ingested / uncached $\rightarrow$ **`needs_hitl_review = True`** with explicit reason code (`UNCACHED_RECORD: First-time ingestion pending human verification`).
4. **Cryptographic Data Bill of Materials (DBOM):** Attach immutable audit trails and SHA-256 hashes to every single cell.

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 9 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Fully Enriched 252-Column Record from Agents 1-8 ]                                             |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. 12-Point Automated Integrity Test Execution                                             │   |
|   │    • Rule 1: Invoice Desc <= 40 chars & ALL CAPS?                                          │   |
|   │    • Rule 2: Mobile Desc between 60 and 80 chars?                                          │   |
|   │    • Rule 3: Brand has proper ® / ™ symbol?                                                │   |
|   │    • Rule 4: Attribute values exist in UniCat LOV?                                         │   |
|   │    • Rule 5: Master UOM spacing validated (e.g. "24 in", not "24in")?                       │   |
|   │ 2. Evidence-Aware 5-Pillar Confidence Engine (Retrieval + Authority + Consistency + ...)   │   |
|   │ 3. Variable-Level Caching Gate: Check active override persistence                          │   |
|   │ 4. Cryptographic Lineage: Generate DBOM SHA-256 Lineage Hash                              │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ├────────────────────────────────────────┬────────────────────────────────────────┐    |
|             ▼ (is_cached == True OR Conf >= 85%)     ▼ (is_cached == False OR Conf < 85%)     |    |
|   ┌──────────────────────────────────┐     ┌─────────────────────────────────────────────────┐|    |
|   │ Automated 252-Column CSV / XLSX  │     │ Human-In-The-Loop (HITL) Review Queue           │|    |
|   │ Delivery Exporter                │     │ • Side-by-side Diff Inspector                   │|    |
|   └──────────────────────────────────┘     │ • 1-Click Approve / Save Override to DuckDB     │|    |
|                                            └─────────────────────────────────────────────────┘|    |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Mathematical Confidence Formulation

$$\text{Confidence} = 0.20 \cdot Q_{\text{retrieval}} + 0.20 \cdot A_{\text{authority}} + 0.20 \cdot C_{\text{consistency}} + 0.20 \cdot S_{\text{agreement}} + 0.20 \cdot V_{\text{validation}} - \text{Pen}_{\text{contradictions}} - \text{Pen}_{\text{missing}}$$

### Sub-Score Vector:
- **$Q_{\text{retrieval}}$ (Retrieval Quality):** 1.00 (Exact KB match), 0.85 (High TF-IDF), 0.50 (Search fallback), 0.40 (Zero match).
- **$A_{\text{authority}}$ (Evidence Authority):** 1.00 (Official PDF/datasheet), 0.95 (Verified OEM domain), 0.80 (Distributor), 0.35 (Unbranded).
- **$C_{\text{consistency}}$ (Extraction Consistency):** 1.00 ($\ge 4$ specs), 0.85 ($2\text{--}3$ specs), 0.70 ($1$ spec), 0.45 ($0$ specs).
- **$S_{\text{agreement}}$ (Cross-Source Consensus):** 1.00 (Full agreement), 0.85 (Inferred), 0.60 (Single source), 0.40 (Conflicting).
- **$V_{\text{validation}}$ (Deterministic Validation):** 1.00 ($12/12$ integrity rules passed; $-0.35$ for each character overflow).

---

## 3. The 12-Point Automated Integrity Suite

| # | Rule Name | Requirement |
| :-: | :--- | :--- |
| **1** | Invoice Length Ceiling | `INVOICE_DESC` $\le 40$ characters |
| **2** | Invoice Casing Check | `INVOICE_DESC` must be 100% UPPERCASE |
| **3** | Mobile Description Window | `MOBILE_DESC` strictly between 60 and 80 characters |
| **4** | Trademark Symbol Audit | `BRAND_NAME` carries legal `®` or `™` |
| **5** | UOM Spacing Validation | Single space between number and unit (e.g. `24 in`) |
| **6** | Fractional Dimension Standard | Inch dimensions use standardized fraction hyphens (`50-1/4 in`) |
| **7** | LOV Vocabulary Conformance | Attribute labels/values strictly match UniCat LOV |
| **8** | Forbidden Marketplace Filter | Prohibits Amazon, eBay, Walmart links in `MFR URL` |
| **9** | Mandatory Identifier Check | `PART_NUMBER`, `Mfg_Part_Num`, `Classpath` populated |
| **10**| 50-Triple Attribute Alignment | Proper triple pairing across `ATTRIBUTE_LABEL/VALUE/UOM 1..50` |
| **11**| Digital Asset Naming | Matches `<CleanBrand>_<MPN>.jpg` & `.pdf` |
| **12**| Leaf UNSPSC Validity | 8-digit leaf commodity code assigned |
