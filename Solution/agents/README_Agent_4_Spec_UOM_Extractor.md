# 📐 Agent 4: Deterministic Spec, Dimension & UOM Extraction Agent
### *OmniSpec AI — Master UOM Standards & Decimal-to-Fraction Normalization Engine*

---

## 1. Agent Overview & Role

The **Deterministic Spec, Dimension & UOM Extraction Agent** parses technical parameters, physical dimensions, electrical ratings, acoustic levels, and industrial packaging configurations from raw descriptions. Industrial B2B buyers search and filter by exact fractions (e.g. `50-1/4 in`, `4-1/2 in`, `7/8 in`) while manufacturers frequently publish decimal strings (`50.25`, `4.5`, `0.875`).

### Core Objectives:
1. **Dimension Triplet Parsing:** Accurately extract complex industrial dimensions (e.g., `4-1/2"x.045"x7/8"`, `1x12-12'`, `24 in W x 24-1/4 in D x 33-7/16 in H`).
2. **Master UOM Standardization:** Enforce the **500+ approved Unit of Measure abbreviations** across 89 measurement categories (e.g., convert `inches`, `IN.`, `inch` to `in`; `feet`, `FT` to `ft`; `amperes`, `Amps` to `A`; `volts`, `V.` to `V`).
3. **UOM Spacing Governance:** Guarantee a strict single space between numeric values and unit symbols (`24 in`, not `24in`; `15 A`, not `15A`; `120 V`, not `120V`).
4. **Decimal-to-Fraction Engine:** Implement the **63 exact inch conversions** from `1/64` (`0.015625`) to `63/64` (`0.984375`) using fractional hyphenated formatting (`50-1/4 in`, not `50.25 in`).
5. **Physical Dimension Mapping:** Populate target physical columns: `LENGTH`, `HEIGHT`, `WIDTH`, `WEIGHT`, `VOLUME` and their corresponding `_UOM` fields.

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 4 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Cleaned Description & Raw Tokens from Agent 1 ]                                                |
|   • "Milw 4-1/2""x.045""x7/8"" Perform+ Metal Cut Off Disc 10pc"                                   |
|   • "24 in W x 24-1/4 in D, 50.25 in Depth With Door Open, 120V 15A 47dBA"                         |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Regex Dimension Parser: Extract [Diameter: 4-1/2", Thickness: .045", Arbor: 7/8"]       │   |
|   │ 2. Electrical & Acoustic Tokenizer: Extract [120V, 15A, 47dBA]                             │   |
|   │ 3. Decimal-to-Fraction Converter: 50.25 in ──► 50-1/4 in                                   │   |
|   │ 4. Master UOM Normalizer: 120V ──► 120 V, 15A ──► 15 A, 47dBA ──► 47 dBA                   │   |
|   │ 5. Physical Dimension Allocator: [Width: 24 in, Depth: 24-1/4 in, Height: 33-7/16 in]      │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ▼                                                                                      |
|   [ Normalized Specs, Fractions & Physical Dimensions ] ───► Handed off to Agent 6 & Agent 7       |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Description / Example |
| :--- | :--- | :--- |
| `cleaned_part_desc` | Agent 1 | `Milw 4-1/2"x.045"x7/8" Perform+ Metal Cut Off Disc 10pc` |
| `extracted_token_bag`| Agent 1 | `{"dimensions": ["4-1/2\"x.045\"x7/8\""], "pack_qty": "10pc"}` |
| `raw_specs_from_oem` | Agent 5 | Optional raw spec dictionary from OEM PDF scraping |

---

## 3. Reference Standards & Conversion Tables

### 3.1 Decimal to Fraction Conversion Table (63 Exact Entries)
Indexed from `Decimal_Fraction.xlsx`:

| Decimal | Fraction | Worked Example |
| :--- | :--- | :--- |
| `0.015625` | `1/64` | `0.015625 in` $\rightarrow$ `1/64 in` |
| `0.03125` | `1/32` | `0.03125 in` $\rightarrow$ `1/32 in` |
| `0.046875` | `3/64` | `0.045 in` $\approx$ `.045 in` |
| `0.0625` | `1/16` | `0.0625 in` $\rightarrow$ `1/16 in` |
| `0.125` | `1/8` | `6.125 in` $\rightarrow$ `6-1/8 in` |
| `0.25` | `1/4` | `50.25 in` $\rightarrow$ `50-1/4 in` |
| `0.375` | `3/8` | `0.375 in` $\rightarrow$ `3/8 in` |
| `0.5` | `1/2` | `4.5 in` $\rightarrow$ `4-1/2 in` |
| `0.75` | `3/4` | `0.75 in` $\rightarrow$ `3/4 in` |
| `0.875` | `7/8` | `0.875 in` $\rightarrow$ `7/8 in` |

### 3.2 Master UOM Standards Rules
- **Rule 1 (Spacing):** Always insert a space between numeric magnitude and unit abbreviation: `24 in` (NOT `24in`), `120 V` (NOT `120V`), `15 A` (NOT `15A`), `47 dBA` (NOT `47dBA`).
- **Rule 2 (Hyphenation in Mixed Fractions):** Whole numbers and fractions are joined by a hyphen: `50-1/4 in` (NOT `50 1/4 in` and NOT `50.25 in`).
- **Rule 3 (Approved Casing):**
  - Length/Width/Height: `in`, `ft`, `yd`, `mm`, `cm`, `m`
  - Electrical: `V`, `A`, `W`, `kW`, `kW-hr`, `Hz`, `VAC`, `VDC`
  - Acoustic: `dBA`
  - Weight: `lb`, `oz`, `kg`, `g`
  - Flow / Speed: `gpm`, `rpm`, `cfm`

---

## 4. Detailed Processing Logic & Algorithms

```python
import re
from fractions import Fraction

class UOMAndFractionEngine:
    DECIMAL_TO_FRACTION_MAP = {
        0.015625: "1/64", 0.03125: "1/32", 0.046875: "3/64", 0.0625: "1/16",
        0.125: "1/8", 0.1875: "3/16", 0.25: "1/4", 0.3125: "5/16",
        0.375: "3/8", 0.4375: "7/16", 0.5: "1/2", 0.5625: "9/16",
        0.625: "5/8", 0.6875: "11/16", 0.75: "3/4", 0.8125: "13/16",
        0.875: "7/8", 0.9375: "15/16"
    }

    @classmethod
    def convert_decimal_to_fraction_str(cls, val: float, uom: str = "in") -> str:
        whole = int(val)
        remainder = round(val - whole, 6)
        
        if remainder == 0:
            return f"{whole} {uom}"
        
        # Check exact lookup table first
        if remainder in cls.DECIMAL_TO_FRACTION_MAP:
            frac_str = cls.DECIMAL_TO_FRACTION_MAP[remainder]
        else:
            # Nearest 64th fraction
            frac = Fraction(remainder).limit_denominator(64)
            frac_str = f"{frac.numerator}/{frac.denominator}"
        
        if whole > 0:
            return f"{whole}-{frac_str} {uom}"
        return f"{frac_str} {uom}"

    @classmethod
    def normalize_uom_spacing(cls, text: str) -> str:
        # Enforce space before standard units
        pattern = r"(\d+(?:[/-]\d+)?(?:\.\d+)?)\s*(in|ft|mm|cm|V|A|W|kW-hr|dBA|lb|oz|gpm|rpm)\b"
        return re.sub(pattern, r"\1 \2", text, flags=re.IGNORECASE)
```

---

## 5. Output Schema & Target Column Mapping

| Target 252-Column Field | Value Example (Dishwasher) | Value Example (Cut-Off Disc) |
| :--- | :--- | :--- |
| `LENGTH` | `24` | `4-1/2` |
| `LENGTH_UOM` | `in` | `in` |
| `WIDTH` | `24-1/4` | `.045` |
| `WIDTH_UOM` | `in` | `in` |
| `HEIGHT` | `33-7/16` | `7/8` |
| `HEIGHT_UOM` | `in` | `in` |
| `WEIGHT` | `78` | `0.15` |
| `WEIGHT_UOM` | `lb` | `lb` |
| `Selling Qty` | `1` | `10` |
| `Selling UOM` | `Each` | `Pack` |

---

## 6. Worked Test Cases

### Case 1: Dimension Triplet with Fractional Normalization
- **Raw Input:** `"49-94-0013 Milw 5""x.045""x7/8"" Metal Cut Off Disc"`
- **Extracted Metrics:**
  - Diameter / Length: `5 in`
  - Thickness / Width: `.045 in`
  - Arbor Hole / Height: `7/8 in`
- **Output:**
  - `LENGTH`: `5`, `LENGTH_UOM`: `in`
  - `WIDTH`: `.045`, `WIDTH_UOM`: `in`
  - `HEIGHT`: `7/8`, `HEIGHT_UOM`: `in`

### Case 2: Dishwasher Dimension & Electrical String
- **Raw Input:** `"24 in W x 24.25 in D, 50.25 in Depth With Door Open, 120V 15A 47dBA"`
- **Processed Metrics:**
  - Width: `24 in`
  - Depth: `24-1/4 in` (`24.25` $\rightarrow$ `24-1/4`)
  - Door Open Depth: `50-1/4 in` (`50.25` $\rightarrow$ `50-1/4`)
  - Voltage: `120 V`
  - Current: `15 A`
  - Sound: `47 dBA`
