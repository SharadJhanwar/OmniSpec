# 📥 Agent 1: Ingestion, De-Noising & Tokenizer Agent
### *OmniSpec AI — Data Cleaning, Placeholder Stripping & Lexical Pre-Processing Engine*

---

## 1. Agent Overview & Role

The **Ingestion, De-Noising & Tokenizer Agent** serves as the initial gatekeeper for the OmniSpec AI enrichment pipeline. Raw distributor data feeds arrive contaminated with non-standard delimiters, placeholder values (e.g. `-- Unbranded --`), cryptic abbreviations, supplier-specific vendor codes (e.g. `Freud Inc (2435)`), and merged dimension tokens (e.g. `1nx6-16'`).

### Core Objectives:
1. **Placeholder Eradication:** Detect and purge negative placeholders across brand/supplier columns.
2. **Deterministic Tokenization:** Split unstructured `Part_Desc` strings into categorized tokens (MPN prefix, Brand mention, Dimension blocks, Technical keywords, Noise tokens).
3. **Supplier Code Separation:** Separate corporate vendor suffixes (e.g. `(2435)`, `(JAMIN)`, `(BOICA)`) from legal manufacturer names.
4. **De-duplication & Hashing:** Generate SHA-256 fingerprint hashes for row-level idempotency and incremental processing.

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 1 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Raw Supplier Row ]                                                                             |
|   • Part_Desc: "DCB518ASTS06G Diablo 1/2""x18"" - Sanding Belt 6pc"                                |
|   • Part_Manuf: "Freud Inc (2435)"                                                                 |
|   • E1_Brand / Unilog_Brand: "-- Unbranded --", "-- No Unilog Brand --"                            |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Placeholder Stripper: Replace placeholders with NULL                                    │   |
|   │ 2. Supplier Code Parser: Extract "Freud Inc" + Supplier Code "2435"                        │   |
|   │ 3. MPN Extractor: Detect prefix "DCB518ASTS06G"                                            │   |
|   │ 4. Dimension Tokenizer: Isolate '1/2"x18"', '6pc', 'Sanding Belt'                          │   |
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
    r"^--\s*None\s*--$",
    r"^--\s*N/A\s*--$",
    r"^UNKNOWN$",
    r"^UNASSIGNED$",
    r"^\s*$"
]
```
If a match is found, the value is set to `None` to prevent downstream models from hallucinating `Unbranded` as a legitimate manufacturer brand.

### Step 2: Supplier Vendor Code Extraction
Supplier strings often append ERP account codes in parentheses: `Freud Inc (2435)`, `Jam Industrial Supply LLC (JAMIN)`, `Milwaukee Accessory (4031)`.
- **Regex:** `r"^(?P<clean_manuf>.*?)\s*\((?P<vendor_code>[A-Za-z0-9]+)\)$"`
- **Result:**
  - `clean_manuf`: `"Freud Inc"`
  - `vendor_code`: `"2435"`

### Step 3: MPN & Description De-noising
1. **Redundant MPN Prefix Removal:** If `Part_Desc` begins with `Mfg_Part_Num`, the duplicate prefix is tokenized as `MPN_TOKEN` and stripped from the active description to isolate technical attributes:
   - Input: `"DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc"`
   - Extracted MPN: `"DCB518ASTS06G"`
   - Remaining Desc: `"Diablo 1/2"x18" - Sanding Belt 6pc"`
2. **Symbol & Delimiter Normalization:**
   - Standardizes escaped quotes: `1/2""x18""` $\rightarrow$ `1/2"x18"`.
   - Normalizes hyphens & en-dashes: ` - ` $\rightarrow$ delimiter split token.
   - Cleans erroneous spacing around dimensions: `1nx6-16'` $\rightarrow$ `1 in x 6 in x 16 ft`.

### Step 4: Token Bag Segmentation
The agent decomposes the string into structured token types:
- **BRAND_CANDIDATE:** `["Diablo", "Freud"]`
- **DIMENSION_CANDIDATE:** `["1/2\"x18\"", "6pc"]`
- **PRODUCT_TYPE_CANDIDATE:** `["Sanding Belt"]`

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
    "keywords": ["Sanding", "Belt"]
  },
  "is_valid": true
}
```

---

## 5. Edge Cases & Fallback Handling

| Edge Case | Raw Example | Handling Strategy |
| :--- | :--- | :--- |
| **All Brand Fields Empty** | `E1_Brand: -- Unbranded --`, `Part_Manuf: ""` | Agent parses `Part_Desc` for embedded brand tokens (`Diablo`, `Milw`, `3M`). |
| **Malformed Dimension Spacing** | `1nx6-16'` or `7/8nx6-20'` | Regex normalizer intercepts `nx` and converts to `in x`. |
| **Double Quote Escapes** | `Diablo 1/2""x18""` | Replace double quotation characters `""` with single `"`. |
| **Distributor Name as MFR** | `Jam Industrial Supply LLC (JAMIN)` | Flags for Agent 2 to resolve actual OEM (e.g. `3M™`). |

---

## 6. Worked Test Case

### Test Input:
```csv
Mfg_Part_Num: 49-94-0101
Part_Desc: "49-94-0101 Milw 4-1/2""x.045""x7/8"" Perform+ Metal Cut Off Disc 10pc"
E1_Brand: -- Unbranded --
Unilog_Brand: -- No Unilog Brand --
DIB_Brand: -- No DIB Brand --
Part_Manuf: Milwaukee Accessory (4031)
```

### Agent 1 Execution:
1. **Placeholder Filter:** `E1_Brand`, `Unilog_Brand`, `DIB_Brand` $\rightarrow$ `None`.
2. **Supplier Split:** `Part_Manuf` $\rightarrow$ Name: `"Milwaukee Accessory"`, Code: `"4031"`.
3. **MPN Strip:** Strip `"49-94-0101"` from description $\rightarrow$ `"Milw 4-1/2"x.045"x7/8" Perform+ Metal Cut Off Disc 10pc"`.
4. **Tokenization:**
   - Brand Token: `"Milw"` $\rightarrow$ Candidate for `Milwaukee`.
   - Dimension Token: `"4-1/2\"x.045\"x7/8\""`.
   - Series Token: `"Perform+"` $\rightarrow$ `"Performance+"`.
   - Category Token: `"Metal Cut Off Disc"`.
   - Packaging Token: `"10pc"`.
