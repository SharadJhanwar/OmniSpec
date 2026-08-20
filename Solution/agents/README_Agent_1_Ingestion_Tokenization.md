# 📥 Agent 1: Ingestion, De-Noising & Tokenizer Agent
### *OmniSpec AI — Data Cleaning, Placeholder Stripping & Lexical Pre-Processing Engine*

---

## 1. Agent Overview & Role

The **Ingestion, De-Noising & Tokenizer Agent** serves as the initial gatekeeper for the OmniSpec AI enrichment pipeline. Raw distributor data feeds arrive contaminated with non-standard delimiters, placeholder values (e.g. `-- Unbranded --`), cryptic abbreviations, supplier-specific vendor codes (e.g. `Freud Inc (2435)`), merged dimension tokens (e.g. `1nx6-16'`), and informal contractor slang (e.g. `sawzall`, `zipper disc`, `romex`).

### Core Objectives:
1. **Placeholder Eradication:** Detect and purge negative placeholders across brand/supplier columns.
2. **Deterministic Tokenization:** Split unstructured `Part_Desc` strings into categorized tokens (MPN prefix, Brand mention, Dimension blocks, Technical keywords, Noise tokens).
3. **Trade Slang & Thesaurus Mapping:** Resolve informal jobsite slang (`sawzall`, `skilsaw`, `zipper disc`, `romex`, `whirlybird`) against the DuckDB `industry_thesaurus` table into canonical product classifications.
4. **Supplier Code Separation:** Separate corporate vendor suffixes (e.g. `(2435)`, `(JAMIN)`, `(BOICA)`) from legal manufacturer names.
5. **De-duplication & Hashing:** Generate SHA-256 fingerprint hashes for row-level idempotency and incremental processing.

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 1 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Raw Supplier Row ]                                                                             |
|   • Part_Desc: "DCB518ASTS06G Diablo 1/2""x18"" - Sanding Belt 6pc sawzall"                        |
|   • Part_Manuf: "Freud Inc (2435)"                                                                 |
|   • E1_Brand / Unilog_Brand: "-- Unbranded --", "-- No Unilog Brand --"                            |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Placeholder Stripper: Replace placeholders with NULL                                    │   |
|   │ 2. Supplier Code Parser: Extract "Freud Inc" + Supplier Code "2435"                        │   |
|   │ 3. MPN Extractor: Detect prefix "DCB518ASTS06G"                                            │   |
|   │ 4. Dimension Tokenizer: Isolate '1/2"x18"', '6pc', 'Sanding Belt'                          │   |
|   │ 5. Industry Thesaurus: Map 'sawzall' -> ('Reciprocating Saw', 'Power Tools')               │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ▼                                                                                      |
|   [ Cleaned Token Bag & Normalized Input State ] ───► Handed off to Agent 2 & Agent 4             |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Input Schema & Data Contract

| Field Name | Type | Presence | Sample Input Value |
| :--- | :--- | :--- | :--- |
| `Mfg_Part_Num` | `string` | Mandatory | `DCB518ASTS06G` |
| `Part_Desc` | `string` | Mandatory | `DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc` |
| `E1_Brand` | `string` | Optional | `-- Unbranded --` |
| `Unilog_Brand`| `string` | Optional | `-- No Unilog Brand --` |
| `DIB_Brand` | `string` | Optional | `-- No DIB Brand --` |
| `Part_Manuf` | `string` | Optional | `Freud Inc (2435)` |
| `SKU` | `string` | Optional | `1515863` |

---

## 3. Detailed Processing Logic & Algorithms

### Step 1: Placeholder Eradication Engine
The agent checks all brand and text fields against a compiled list of negative placeholders:
```python
PLACEHOLDER_PATTERNS = [
    r"^--\s*Unbranded\s*--$",
    r"^--\s*No\s+Unilog\s+Brand\s*--$",
    r"^--\s*No\s+DIB\s+Brand\s*--$",
    r"^--\s*No\s+Brand\s*--$",
    r"^UNKNOWN$",
    r"^N/A$",
    r"^NONE$"
]
```

### Step 2: Supplier String & Vendor Code Parser
Extracts clean corporate names while isolating numerical distributor account codes:
- Pattern: `r"^(.*?)\s*\(([A-Za-z0-9]+)\)$"`
- Input: `"Appliance Dealers Cooperative (APPDE)"` $\rightarrow$ Name: `"Appliance Dealers Cooperative"`, Vendor Code: `"APPDE"`.
- Input: `"Milwaukee Accessory (4031)"` $\rightarrow$ Name: `"Milwaukee Accessory"`, Vendor Code: `"4031"`.

### Step 3: MPN Duplicate Stripping & Normalization
1. **Redundant MPN Prefix Removal:** If `Part_Desc` begins with `Mfg_Part_Num`, the duplicate prefix is tokenized as `MPN_TOKEN` and stripped from the active description to isolate technical attributes.
2. **Symbol & Delimiter Normalization:**
   - Standardizes escaped quotes: `1/2""x18""` $\rightarrow$ `1/2"x18"`.
   - Normalizes hyphens & en-dashes: ` - ` $\rightarrow$ delimiter split token.
   - Cleans erroneous spacing around dimensions: `1nx6-16'` $\rightarrow$ `1 in x 6 in x 16 ft`.

### Step 4: Token Bag Segmentation
The agent decomposes the string into structured token types:
- **BRAND_CANDIDATE:** `["Diablo", "Freud"]`
- **DIMENSION_CANDIDATE:** `["1/2\"x18\"", "6pc"]`
- **PRODUCT_TYPE_CANDIDATE:** `["Sanding Belt"]`

### Step 5: Industry Slang & Contractor Thesaurus Resolution
Queries the DuckDB `industry_thesaurus` table to translate common contractor jargon:
- `"sawzall"` $\rightarrow$ `("Reciprocating Saw", "Power Tools")`
- `"skilsaw"` $\rightarrow$ `("Circular Saw", "Power Tools")`
- `"zipper disc"` $\rightarrow$ `("Cut-Off Disc", "Abrasives")`
- `"romex"` $\rightarrow$ `("Non-Metallic Sheathed Cable", "Electrical")`
- `"whirlybird"` $\rightarrow$ `("Roof Turbine Vent", "Building Materials")`

---

## 4. Output Schema & Downstream Contracts

```json
{
  "row_id": "row_001",
  "row_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "clean_mfg_part_num": "DCB518ASTS06G",
  "raw_part_desc": "DCB518ASTS06G Diablo 1/2\"x18\" - Sanding Belt 6pc",
  "cleaned_part_desc": "Diablo 1/2\"x18\" - Sanding Belt 6pc",
  "clean_supplier_name": "Freud Inc",
  "supplier_vendor_code": "2435",
  "brand_candidates": ["Diablo", "Freud Inc"],
  "extracted_token_bag": {
    "dimensions": ["1/2\"x18\""],
    "pack_qty": "6pc",
    "keywords": ["Sanding", "Belt"],
    "thesaurus": null
  },
  "is_valid": true
}
```
