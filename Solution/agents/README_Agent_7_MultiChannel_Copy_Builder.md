# ✍️ Agent 7: Multi-Channel Formulaic Copy Builder Agent
### *OmniSpec AI — Deterministic Multi-Tier Copy Construction & Length-Constraint Engine*

---

## 1. Architectural Blueprint & Component Topology

```mermaid
flowchart TD
    subgraph COPY_INPUT ["📥 Normalized Data & Attribute Triples"]
        A2_BRAND["Canonical Brand & MFR (from Agent 2)"]
        A3_PNAME["Product Name & Classpath (from Agent 3)"]
        A4_SPECS["Extracted Specs, Dims & UOMs (from Agent 4)"]
        A6_TRIPLES["Bound Attribute Triples (from Agent 6)"]
    end

    subgraph AGENT_7_CORE ["⚙️ Agent 7 Copy Synthesis Engine (MultiChannelCopyAgent)"]
        direction TB
        STEP1["1. Invoice Description Generator (<= 40 chars ALL CAPS)<br/>• Formula: <NOUN> <SPEC> <MPN><br/>• e.g. 'DISHWASHER SST SHX78B75UC' (25 chars)"]
        STEP2["2. Mobile Description Generator (60-80 chars window)<br/>• Formula: <Brand>, <Item>, Industrial Grade, <MPN><br/>• Strict whitespace padding to guarantee 60-80 chars"]
        STEP3["3. Title / Short Description Assembler<br/>• Formula: Brand® + Series + MPN + Item Type + Key Specs"]
        STEP4["4. Long Description & Additional Info Generator<br/>• Standardized narrative + 'Additional Information:' spec block"]
        STEP5["5. 20-Bullet Feature Allocator<br/>• Formats atomic capability bullets (ITEM_FEATURES_1..20)"]
        
        STEP1 --> STEP2 --> STEP3 --> STEP4 --> STEP5
    end

    subgraph COPY_OUTPUT ["📦 State Delta Output (ProductEnrichmentState)"]
        INVOICE["invoice_desc: 'DISHWASHER SST SHX78B75UC' (len: 25/40)"]
        MOBILE["mobile_desc: 'Bosch®, Dishwasher, Industrial Grade, SHX78B75UC           ' (len: 60)"]
        SHORT["short_desc: 'Bosch® SHX78B75UC Dishwasher'"]
        LONG["long_desc1: 'Bosch® SHX78B75UC Dishwasher, engineered for reliable performance...'"]
        BULLETS["item_features: {'ITEM_FEATURES_1': 'Sound Level: 42 dBA', ...}"]
    end

    COPY_INPUT --> STEP1
    STEP5 --> COPY_OUTPUT
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Example Value |
| :--- | :--- | :--- |
| `BRAND_NAME` | Agent 2 | `Bosch®` |
| `MANUFACTURER_NAME` | Agent 2 | `BSH Home Appliances Corporation` |
| `MANUFACTURER_PART_NUMBER`| Agent 2 | `SHX78B75UC` |
| `Product Name` | Agent 3 | `Dishwasher` |
| `EAV_Attributes` | Agent 6 | `{"Series": "800 Series", "Sound Level": "42 dBA", ...}` |

---

## 3. The 6-Tier Copy Governance Standards

| Tier | Field Name | Character Limit / Format | Formula & Governance Rule |
| :--- | :--- | :--- | :--- |
| **1** | `INVOICE_DESC` | $\le 40$ chars, **ALL CAPS** | `[PRODUCT_NOUN] [KEY_SPEC] [MPN]` |
| **2** | `MOBILE_DESC` | Strictly **$60\text{--}80$ chars** | `[Brand], [Product_Noun], [Series], [MPN]` (Padded) |
| **3** | `SHORT_DESC` | $\le 150$ chars | `[Brand®] [Series] [MPN] [Product Name]` |
| **4** | `LONG_DESC1` | Narrative paragraph | Complete technical narrative + `Additional Information:` |
| **5** | `RETAIL_DESC` | Consumer overview | High-converting marketing copy |
| **6** | `ITEM_FEATURES_1..20`| 20 Atomic Bullet Points | Key specifications, approvals, and mechanical attributes |

---

## 4. Execution Telemetry & Performance
- **Average Latency:** $0.04\text{--}0.15\text{ ms}$ per SKU.
- **Trace Output:** Logs `[Agent 7 ✓] Copy Synthesized (<ms> ms) — INVOICE: '<invoice_desc>' (<len>/40 chars)`.
