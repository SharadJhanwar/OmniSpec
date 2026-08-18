# 🛡️ Agent 9: Quality Audit, Lineage Tracer & HITL Orchestrator Agent
### *OmniSpec AI — 12-Rule Integrity Auditor, Confidence Scoring & Human-In-The-Loop Engine*

---

## 1. Agent Overview & Role

The **Quality Audit, Lineage Tracer & HITL Orchestrator Agent** is the final quality assurance gatekeeper for OmniSpec AI. In enterprise catalog management, unverified AI outputs introduce risk; Agent 9 deterministically tests all 252 generated columns against 12 hard integrity constraints, computes granular confidence scores ($0\text{--}100\%$), tracks cell-level provenance, and routes flagged edge cases to the **Human-In-The-Loop (HITL) Review Studio**.

### Core Objectives:
1. **12-Point Automated Integrity Suite:** Run comprehensive deterministic audits across character limits, casing, symbols, UOM spaces, and LOV validity.
2. **Field-Level & Record-Level Confidence Scoring:** Calculate weighted confidence scores based on source verification and rule compliance.
3. **Cell-Level Lineage & Provenance Tracking:** Attach immutable audit trails to every single cell (e.g. `OEM_PDF_RAG`, `UNICAT_EXACT`, `REGEX_RULE`, `HITL_OVERRIDE`).
4. **HITL Exception Routing & Diff Review:** Stream records with $\text{Confidence} < 85\%$ or rule violations to the interactive Human-In-The-Loop workbench for rapid 1-click approval or inline correction.

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
|   │ 2. Confidence Scoring Engine: Calculate Record Confidence (0-100%)                         │   |
|   │ 3. Lineage Annotation: Tag each cell with extraction method & source URL                   │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ├────────────────────────────────────────┬────────────────────────────────────────┐    |
|             ▼ (Confidence >= 85% & No Rule Errors)   ▼ (Confidence < 85% or Rule Violation)   |    |
|   ┌──────────────────────────────────┐     ┌─────────────────────────────────────────────────┐|    |
|   │ Automated 252-Column CSV / XLSX  │     │ Human-In-The-Loop (HITL) Review Queue           │|    |
|   │ Delivery Exporter                │     │ • Side-by-side Diff Inspector                   │|    |
|   └──────────────────────────────────┘     │ • 1-Click Approve / Inline Cell Override        │|    |
|                                            └─────────────────────────────────────────────────┘|    |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. The 12-Point Automated Integrity Suite

```
+----------------------------------------------------------------------------------------------------+
|                                 12 AUTOMATED INTEGRITY RULES                                       |
+----+--------------------------------+--------------------------------------------------------------+
| #  | RULE NAME                      | GOVERNANCE REQUIREMENT                                       |
+----+--------------------------------+--------------------------------------------------------------+
| 1  | Invoice Length Ceiling         | INVOICE_DESC must be <= 40 characters                        |
| 2  | Invoice Casing Check           | INVOICE_DESC must be 100% UPPERCASE                          |
| 3  | Mobile Description Window      | MOBILE_DESC must be strictly between 60 and 80 characters    |
| 4  | Trademark Symbol Audit         | BRAND_NAME must match UniCat legal symbol (® / ™)            |
| 5  | UOM Spacing Validation         | Must have single space between number and unit (e.g. 24 in)  |
| 6  | Fractional Dimension Standard  | Inch dimensions must use fractional hyphens (50-1/4 in)      |
| 7  | LOV Vocabulary Conformance     | All ATTRIBUTE_LABEL and VALUES must exist in UniCat LOV      |
| 8  | Sourcing Hierarchy Gate        | MFR URL must be official OEM domain (no Amazon, Grainger)    |
| 9  | Mandatory Identifier Audit     | MANUFACTURER_NAME, BRAND_NAME, MPN, Classpath must not be NULL|
| 10 | Asset Naming Syntax            | Images & PDFs must follow <Brand>_<MPN>.<ext> format         |
| 11 | Feature Bullet Cleanliness     | ITEM_FEATURES_1..20 must not contain trailing delimiters     |
| 12 | Duplicate SKU Guard            | PART_NUMBER and Mfg_Part_Num must be unique within batch     |
+----+--------------------------------+--------------------------------------------------------------+
```

---

## 3. Confidence Scoring Algorithm

The record confidence score $C_{\text{record}}$ is computed as a weighted average across core functional tiers:

$$C_{\text{record}} = 0.25 C_{\text{brand}} + 0.20 C_{\text{taxonomy}} + 0.25 C_{\text{attributes}} + 0.15 C_{\text{copy}} + 0.15 C_{\text{sourcing}}$$

Where:
- $C_{\text{brand}} = 1.0$ if matched directly to UniCat 27K; $0.8$ if fuzzy matched.
- $C_{\text{taxonomy}} = 1.0$ if leaf node matches UniCat LOV; $0.5$ if inferred.
- $C_{\text{attributes}} = \frac{\text{Number of LOV-Compliant Attributes}}{\text{Total Extracted Attributes}}$.
- $C_{\text{copy}} = 1.0 - 0.25 \times (\text{Number of Copy Rule Violations})$.
- $C_{\text{sourcing}} = 1.0$ if official OEM URL verified; $0.0$ if unverified.

---

## 4. Cell-Level Lineage & Provenance Metadata

Every cell in the 252-column output is backed by a structured provenance object:

```json
{
  "field": "Sound Level",
  "value": "47",
  "uom": "dBA",
  "confidence": 0.98,
  "extraction_method": "OEM_PDF_RAG",
  "source_document": "https://www.frigidaire.com/en/p/owner-center/product-support/PDSH4816AF",
  "source_page": 2,
  "lov_canonical_match": true,
  "human_reviewed": false
}
```

---

## 5. Human-In-The-Loop (HITL) Workflow & UI Payload

When an item fails an integrity check or $C_{\text{record}} < 0.85$, Agent 9 generates an interactive review payload:

```json
{
  "sku": "1515863",
  "mfg_part_num": "PDSH4816AF",
  "overall_confidence": 0.78,
  "violations": [
    {
      "rule": "RULE_3_MOBILE_DESC_WINDOW",
      "current_value": "Rheem Manufacturing FRIGIDAIRE, Dishwasher, PDSH4816AF",
      "char_count": 54,
      "expected_range": [60, 80],
      "suggested_fix": "Rheem Manufacturing FRIGIDAIRE, Dishwasher, Professional Series, PDSH4816AF"
    }
  ],
  "diff_view": {
    "raw_input": "PDSH4816AF Dishwasher SS - Display Only",
    "ai_generated": "FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With CleanBoost™, Leg Mounting, 5-Wash Cycle, Stainless Steel",
    "status": "AWAITING_REVIEW"
  }
}
```

### Reviewer Capabilities:
1. **1-Click Suggestion Acceptance:** Reviewer clicks "Apply Fix" to update the field and recalculate confidence.
2. **Inline Cell Editing:** Edit any of the 252 columns directly within the virtualized AG Grid.
3. **Audit History Log:** Saves operator timestamp and reason for all overrides.

---

## 6. Worked Test Case

### Case: Invoice Length Violation Auto-Remediation
- **Initial Generated Invoice Desc:** `FRIGIDAIRE PROFESSIONAL 5-CYCLE STAINLESS DISHWASHER` (Length: 53 chars $\gt 40$) $\rightarrow$ **FAIL (Rule 1)**.
- **Agent 9 Trigger:** Activates abbreviation condenser:
  - `FRIGIDAIRE` $\rightarrow$ Omitted (Item type takes precedence)
  - `PROFESSIONAL` $\rightarrow$ Omitted
  - `5-CYCLE` $\rightarrow$ `5`
  - `STAINLESS` $\rightarrow$ `SST`
  - `LEG MOUNTING` $\rightarrow$ `LEG`
  - `120V 15A` $\rightarrow$ `120V 15A`
  - `50-1/4IN` $\rightarrow$ `50-1/4IN`
- **Remediated Value:** `DISHWASHER LEG 5 SST 120V 15A 50-1/4IN` (Length: 37 chars $\le 40$) $\rightarrow$ **PASS**.
- **Final Confidence Score:** $98.5\%$.
