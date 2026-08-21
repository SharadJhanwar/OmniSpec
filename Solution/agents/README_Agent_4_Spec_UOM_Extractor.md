# 📐 Agent 4: Deterministic Spec, Dimension & UOM Extraction Agent
### *OmniSpec AI — Master UOM Standards & Decimal-to-Fraction Normalization Engine*

---

## 1. Architectural Blueprint & Component Topology

```mermaid
flowchart TD
    subgraph SPEC_INPUT ["📥 Raw Tokens & Grounded Text"]
        RAW_DESC["Cleaned Description (from Agent 1)"]
        OEM_GROUND["OEM Grounded Snippets (from Agent 5 / DuckDB)"]
    end

    subgraph AGENT_4_CORE ["⚙️ Agent 4 Dimension & Spec Engine (SpecUOMExtractorAgent)"]
        direction TB
        STEP1["1. Multi-Format Dimension Parser<br/>• Regex extracts 3D blocks (4-1/2\"x.045\"x7/8\", 1x12-12')<br/>• Extracts explicit L/W/H (24 in W x 24-1/4 in D x 33-7/16 in H)"]
        STEP2["2. 63-Entry Decimal-to-Fraction Hashmap<br/>• Converts 0.25 → 1/4 in, 0.5 → 1/2 in, 0.875 → 7/8 in<br/>• Standardizes hyphenated compound inches (50.25 in → 50-1/4 in)"]
        STEP3["3. Master UOM Single-Space Normalizer<br/>• Maps 500+ unit abbreviations (inches, IN, inch → in)<br/>• Enforces single space constraint (24in → 24 in, 120V → 120 V, 47dBA → 47 dBA)"]
        STEP4["4. Domain-Specific Spec Extractors<br/>• Electrical: Voltage (120 V), Amperage (15 A), Power (1800 W)<br/>• Acoustic: Sound Level (42 dBA / 47 dBA)<br/>• Hydraulic: Flow Rate (50 GPM), Pressure (150 PSI)<br/>• Packaging: Selling Qty ('1'), Selling UOM ('Each')"]
        
        STEP1 --> STEP2 --> STEP3 --> STEP4
    end

    subgraph SPEC_OUTPUT ["📦 State Delta Output (ProductEnrichmentState)"]
        DIMS["dimensions: {'LENGTH': '24', 'WIDTH': '24', 'HEIGHT': '34', 'DIMENSION_UOM': 'in'}"]
        ELEC["electrical_specs: {'VOLTAGE': '120', 'AMPERAGE': '15', 'VOLTAGE_UOM': 'V'}"]
        ACOUSTIC["acoustic_specs: {'Sound Level': '42', 'Sound Level UOM': 'dBA'}"]
        PACK["packaging: {'Selling Qty': '1', 'Selling UOM': 'Each', 'Standard Packaging Information': '1 Each'}"]
    end

    SPEC_INPUT --> STEP1
    STEP4 --> SPEC_OUTPUT
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Description / Example |
| :--- | :--- | :--- |
| `cleaned_part_desc` | Agent 1 | `Milw 4-1/2"x.045"x7/8" Perform+ Metal Cut Off Disc 10pc` |
| `extracted_token_bag`| Agent 1 | `{"dimensions": ["4-1/2\"x.045\"x7/8\""], "pack_qty": "10pc"}` |
| `raw_specs_from_oem` | Agent 5 | Optional raw spec dictionary from OEM PDF scraping |

---

## 3. Decimal to Fraction Conversion Standards (63 Exact Entries)

Indexed from `Decimal_Fraction.xlsx`:

| Decimal | Fraction | Worked Example |
| :--- | :--- | :--- |
| `0.015625` | `1/64` | `0.015625 in` $\rightarrow$ `1/64 in` |
| `0.03125` | `1/32` | `0.03125 in` $\rightarrow$ `1/32 in` |
| `0.046875` | `3/64` | `0.045 in` $\approx$ `.045 in` |
| `0.0625` | `1/16` | `0.0625 in` $\rightarrow$ `1/16 in` |
| `0.125` | `1/8` | `0.125 in` $\rightarrow$ `1/8 in` |
| `0.25` | `1/4` | `0.25 in` $\rightarrow$ `1/4 in` |
| `0.5` | `1/2` | `0.5 in` $\rightarrow$ `1/2 in` |
| `0.75` | `3/4` | `0.75 in` $\rightarrow$ `3/4 in` |
| `0.875` | `7/8` | `0.875 in` $\rightarrow$ `7/8 in` |

---

## 4. Master UOM Single-Space Governance

Unilog standards strictly mandate a **single space** between numerical measurements and approved unit abbreviations:

| Measurement Type | Raw Contaminated Input | Normalized Standard | Master UOM |
| :--- | :--- | :--- | :--- |
| **Length / Diameter** | `24in`, `24"`, `24 INCHES`, `24inch` | `24 in` | `in` |
| **Electrical Voltage** | `120V`, `120 Volts`, `120v` | `120 V` | `V` |
| **Electrical Current** | `15A`, `15 Amps`, `15amp` | `15 A` | `A` |
| **Acoustic Noise** | `42dBA`, `42 dbA`, `42 dba` | `42 dBA` | `dBA` |
| **Rotational Speed** | `12000RPM`, `12000 rpm` | `12000 RPM` | `RPM` |
| **Hydraulic Flow** | `50GPM`, `50 gpm` | `50 GPM` | `GPM` |

---

## 5. Execution Telemetry & Performance
- **Average Latency:** $0.1\text{--}0.5\text{ ms}$ per SKU.
- **Trace Output:** Logs `[Agent 4 ✓] Specs Extracted (<ms> ms)`.
