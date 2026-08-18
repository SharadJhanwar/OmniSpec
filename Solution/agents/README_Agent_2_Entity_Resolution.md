# 🏷️ Agent 2: Brand & Entity Resolution Agent
### *OmniSpec AI — UniCat 27K Master Entity Resolution & Trademark Normalization Engine*

---

## 1. Agent Overview & Role

The **Brand & Entity Resolution Agent** is responsible for establishing the definitive manufacturer, legal brand, and trademark identity for every catalog item. Raw distributor feeds frequently list third-party distributors (e.g., `Jam Industrial Supply LLC (JAMIN)`, `Appliance Dealers Cooperative (APPDE)`, `Parksite (6151)`) in the manufacturer field while omitting the actual brand or using abbreviations (e.g., `Milw`, `3M`, `TREX`).

### Core Objectives:
1. **Canonical Manufacturer & Brand Resolution:** Map messy supplier text to exact rows in the **27,000+ UniCat Master Database**.
2. **Distributor vs. OEM Disambiguation:** Identify when `Part_Manuf` is merely a wholesale distributor/co-op, and resolve the true OEM manufacturer and brand from the description tokens and MPN patterns.
3. **Legal Casing & Trademark Governance:** Instate strict legal casing, entity suffixes (`Inc`, `LLC`, `Corp`), and mandatory intellectual property symbols (`®`, `™`) as required by the Unilog Content Guidelines.
4. **Manufacturer Part Number (MPN) Standard:** Clean and assign `MANUFACTURER_PART_NUMBER` and `TRADE_NAME`.

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 2 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Cleaned Token Bag from Agent 1 ]                                                               |
|   • Supplier: "Milwaukee Accessory (4031)"                                                         |
|   • Desc Tokens: "Milw", "49-94-0013", "Cut Off Disc"                                              |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Supplier Disambiguation: Check if supplier is distributor or OEM                        │   |
|   │ 2. Brand Keyword Resolution: "Milw" ──► "Milwaukee"                                        │   |
|   │ 3. RapidFuzz C++ Matching against UniCat 27,000+ Table:                                    │   |
|   │    - Match: MANUFACTURER_NAME = "Milwaukee Electric Tool Corporation"                      │   |
|   │    - Match: BRAND_NAME = "Milwaukee®"                                                      │   |
|   │ 4. Symbol Injection: Ensure mandatory ® / ™ registered marks                               │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ▼                                                                                      |
|   [ Enriched Brand Entity State ] ───► Handed off to Agent 3 (Taxonomy) & Agent 6 (LOV)           |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Description / Example |
| :--- | :--- | :--- |
| `clean_mfg_part_num` | Agent 1 | `49-94-0013` |
| `clean_supplier_name`| Agent 1 | `Milwaukee Accessory` |
| `cleaned_part_desc` | Agent 1 | `Milw 5"x.045"x7/8" Metal Cut Off Disc` |
| `brand_candidates` | Agent 1 | `["Milw", "Milwaukee Accessory"]` |
| `E1_Brand` | Raw Row | `-- Unbranded --` (or raw string if present) |

---

## 3. Knowledge Base & Reference Dependencies

The agent indexes the master **`UniCat_Manufacturer_and_Brand_List.xlsx`** (27,000+ rows):
- `MANUFACTURER_NAME`: Official legal entity name (e.g. `Milwaukee Electric Tool Corporation`, `Rheem Manufacturing`, `Whirlpool Corporation`, `Freud Inc`).
- `MANUFACTURER_CODE`: Standardized MFR code (e.g. `MILW`, `RHEEM`, `WHIRL`).
- `BRAND_NAME`: Controlled brand name with legal symbol (e.g. `Milwaukee®`, `FRIGIDAIRE®`, `Whirlpool®`, `Diablo®`, `3M™`, `TimberTech®`, `Trex®`).
- `BRAND_CODE`: Unique brand identifier.

---

## 4. Detailed Processing Logic & Algorithms

```
+----------------------------------------------------------------------------------------------------+
|                              2-STAGE FUZZY & DISAMBIGUATION ENGINE                                 |
+----------------------------------------------------------------------------------------------------+
|  Input Tokens ──► [ Common Abbreviation Lexicon ] ──► [ RapidFuzz Token Sort (Threshold >= 85) ]   |
|                                                                 │                                  |
|                                                  ┌──────────────┴──────────────┐                   |
|                                                  ▼                             ▼                   |
|                                           [ Exact Match ]            [ Semantic Vector RAG ]       |
|                                                  │                             │                   |
|                                                  └──────────────┬──────────────┘                   |
|                                                                 ▼                                  |
|                                             [ Ingest Legal Casing & Symbols ® / ™ ]                |
+----------------------------------------------------------------------------------------------------+
```

### Step 1: Industrial Abbreviation Expansion
Before querying the 27K database, common industrial short-codes are resolved via a deterministic dictionary:
```python
INDUSTRIAL_BRAND_ALIASES = {
    "MILW": "Milwaukee Electric Tool Corporation",
    "MILWAUKEE": "Milwaukee Electric Tool Corporation",
    "DIABLO": "Freud Inc",
    "3M": "3M Co",
    "FRIG": "Rheem Manufacturing",
    "FRIGIDAIRE": "Rheem Manufacturing",
    "WHIRL": "Whirlpool Corporation",
    "TIMBERTECH": "TimberTech",
    "TREX": "Trex Company Inc",
    "AZEK": "The AZEK Company LLC",
    "MIRKA": "Mirka Abrasives Inc"
}
```

### Step 2: Distributor vs. OEM Detection
Distributor co-ops frequently appear in `Part_Manuf`. The agent flags known distributor entities:
- `Appliance Dealers Cooperative (APPDE)` $\rightarrow$ Look inside `Part_Desc` / `MPN` for OEM (`Rheem Manufacturing` / `FRIGIDAIRE` or `Whirlpool Corporation` / `Whirlpool`).
- `Jam Industrial Supply LLC (JAMIN)` $\rightarrow$ Look inside `Part_Desc` for `3M` $\rightarrow$ Map to `3M Co` / `3M™`.
- `Parksite (6151)` / `U S Lumber (3073)` / `Boise Cascade (BOICA)` $\rightarrow$ Look inside `Part_Desc` for `Trex` or `TimberTech`.

### Step 3: RapidFuzz C++ Matching & Scoring
Matches are computed using token sort and partial ratio algorithms:
$$\text{Score} = \text{RapidFuzz.fuzz.token\_sort\_ratio}(\text{QueryCandidate}, \text{UniCatRecord})$$
- If $\text{Score} \ge 90$: Automatic acceptance.
- If $75 \le \text{Score} < 90$: Contextual tie-breaking with `Classpath` and `MPN` pattern.
- If $\text{Score} < 75$: Fallback to embedding cosine similarity over UniCat catalog.

### Step 4: Trademark Symbol Rules
As defined in Unilog Internal Content Guidelines:
- If UniCat designates a registered brand, the symbol `®` or `™` must be appended with zero space: `FRIGIDAIRE®`, `Milwaukee®`, `3M™`, `Whirlpool®`.
- If no specific brand exists under the manufacturer, the normalized `MANUFACTURER_NAME` is used in place of `BRAND_NAME`.

---

## 5. Output Schema & 252-Column Target Mapping

| 252-Column Field | Value Example 1 | Value Example 2 | Value Example 3 |
| :--- | :--- | :--- | :--- |
| `MANUFACTURER_NAME` | `Rheem Manufacturing` | `Milwaukee Electric Tool Corporation` | `3M Co` |
| `BRAND_NAME` | `FRIGIDAIRE®` | `Milwaukee®` | `3M™` |
| `TRADE_NAME` | `Professional Series` | `Performance+` | `Cubitron™ II` |
| `MANUFACTURER_PART_NUMBER` | `PDSH4816AF` | `49-94-0101` | `7100075678` |
| `ALTERNATE_PART_NUMBER` | `""` | `49940101` | `3MABR-7100075678` |

---

## 6. Worked Test Cases from Dataset

### Case 1: Cryptic Dishwasher Row
- **Input:** `Mfg_Part_Num: PDSH4816AF`, `Part_Manuf: Appliance Dealers Cooperative (APPDE)`, `Part_Desc: PDSH4816AF Dishwasher SS - Display Only`
- **Resolution:**
  - `Part_Manuf` is a distributor co-op (`APPDE`).
  - MPN prefix `PDSH` maps to Frigidaire Professional Series.
  - **Output `MANUFACTURER_NAME`:** `Rheem Manufacturing`
  - **Output `BRAND_NAME`:** `FRIGIDAIRE®`

### Case 2: Abrasive Cut-Off Disc
- **Input:** `Mfg_Part_Num: 49-94-0013`, `Part_Manuf: Milwaukee Accessory (4031)`, `Part_Desc: 49-94-0013 Milw 5"x.045"x7/8" Metal Cut Off Disc`
- **Resolution:**
  - Token `Milw` expanded to Milwaukee.
  - **Output `MANUFACTURER_NAME`:** `Milwaukee Electric Tool Corporation`
  - **Output `BRAND_NAME`:** `Milwaukee®`
