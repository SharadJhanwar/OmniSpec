# ✍️ Agent 7: Multi-Channel Formulaic Copy Builder Agent
### *OmniSpec AI — Deterministic Multi-Tier Copy Construction & Length-Constraint Engine*

---

## 1. Agent Overview & Role

The **Multi-Channel Formulaic Copy Builder Agent** transforms structured attributes into multi-channel commerce copy. In industrial supply chains, a single product record must serve divergent channel endpoints: ERP till receipts, mobile warehouse scanning apps, faceted search engines, and rich e-commerce PDPs (Product Detail Pages).

### Core Objectives:
1. **Invoice Description ($\le 40$ chars, ALL CAPS):** Generate ultra-compact ERP invoice line descriptions respecting strict abbreviations and the 40-character ceiling.
2. **Mobile Description ($60\text{--}80$ chars):** Build scannable strings for mobile warehouse and procurement applications.
3. **Product Title / Short Description:** Assemble strict formulaic product titles:  
   $$\text{Title} = \text{Brand}^\circledR + \text{Series} + \text{MPN} + \text{Item Type} + \text{Key Attributes}$$
4. **Long Description:** Synthesize an exhaustive technical specification narrative including all standardized dimensions, electrical parameters, and an `Additional Information:` section.
5. **Retail & Marketing Descriptions:** Produce high-converting marketing overviews.
6. **Feature Bullets (`ITEM_FEATURES_1..20`):** Extract and format up to 20 atomic, benefit-driven bullet points.

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 7 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Normalized Master Data & Structured EAV Attributes from Agents 2, 4, 5, 6 ]                    |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Invoice Desc Generator: Format UPPERCASE string & verify Length <= 40 chars             │   |
|   │ 2. Mobile Desc Generator: Format '<MFR> <Brand>, <Item>, <Series>, <MPN>' (60-80 chars)    │   |
|   │ 3. Product Title Builder: Execute Unilog Title Formula                                     │   |
|   │ 4. Long Description Assembler: Merge specs into narrative + "Additional Information:"      │   |
|   │ 5. Marketing & Retail Copy Builder: High-converting consumer paragraph                     │   |
|   │ 6. Item Features Allocator: Assign ITEM_FEATURES_1 to ITEM_FEATURES_20                     │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ▼                                                                                      |
|   [ 6 Tiers of Multi-Channel Copy ] ───► Handed off to Agent 8 (Assets) & Agent 9 (Audit)          |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Example Value |
| :--- | :--- | :--- |
| `BRAND_NAME` | Agent 2 | `FRIGIDAIRE®` |
| `MANUFACTURER_NAME` | Agent 2 | `Rheem Manufacturing` |
| `MANUFACTURER_PART_NUMBER`| Agent 2 | `PDSH4816AF` |
| `Product Name` | Agent 3 | `Dishwasher` |
| `With` | Agent 6 | `With CleanBoost™` |
| `EAV_Attributes` | Agent 6 | `{"Series": "Professional Series", "Voltage Rating": "120", "Sound Level": "47", ...}` |

---

## 3. Construction Formulas & Strict Governance Rules

```
+----------------------------------------------------------------------------------------------------+
|                               6-TIER MULTI-CHANNEL COPY SPECIFICATION                              |
+----------------------+-----------------------+-----------------------------------------------------+
| COPY TIER            | CONSTRAINT            | CONSTRUCTION FORMULA                                |
+----------------------+-----------------------+-----------------------------------------------------+
| 1. INVOICE_DESC      | <= 40 Char, ALL CAPS  | <ITEM_TYPE> <MOUNTING> <SPECS> <VOLTS> <AMPS> <DIM> |
| 2. MOBILE_DESC       | 60 to 80 Characters   | <MFR_NAME> <BRAND_NAME>, <ITEM_TYPE>, <SERIES>, <MPN>|
| 3. SHORT_DESC        | Formulaic / Title     | <BRAND>® <SERIES> <MPN> <ITEM_TYPE> <WITH>, <SPECS> |
| 4. LONG_DESC1        | Comprehensive Specs   | <BRAND>® <ITEM_TYPE> <WITH>, <SERIES>, <SPECS_LIST> |
| 5. RETAIL_DESC       | Clean Marketing Title | <SERIES> <ITEM_TYPE>, <MOUNTING>, <SPECS>, <FINISH> |
| 6. ITEM_FEATURES 1-20| Atomic Bullets        | Bulleted technical highlights (one per column)      |
+----------------------+-----------------------+-----------------------------------------------------+
```

### Formula 1: INVOICE_DESC ($\le 40$ Chars, UPPERCASE)
- **Approved Abbreviations:** `DISHWASHER` $\rightarrow$ `DISHWASHER`, `Stainless Steel` $\rightarrow$ `SST`, `Built-in` $\rightarrow$ `BLTLN`, `Leg Mounting` $\rightarrow$ `LEG`, `5-Wash Cycle` $\rightarrow$ `5`.
- **Output:** `DISHWASHER LEG 5 SST 120V 15A 50-1/4IN`  
  *Length Check:* 37 characters $\le 40$ $\rightarrow$ **PASS**.

### Formula 2: MOBILE_DESC ($60\text{--}80$ Chars)
- **Formula:** `<MANUFACTURER_NAME> <BRAND_NAME_CLEAN>, <ITEM_TYPE>, <SERIES>, <MPN>`
- **Output:** `Rheem Manufacturing FRIGIDAIRE, Dishwasher, Professional Series, PDSH4816AF`  
  *Length Check:* 74 characters $\in [60, 80]$ $\rightarrow$ **PASS**.

### Formula 3: SHORT_DESC (Product Title)
- **Formula:** `<BRAND_NAME> <SERIES> <MPN> <PRODUCT_NAME> <WITH>, <MOUNTING> Mounting, <KEY_SPEC>, <FINISH>`
- **Output:** `FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With CleanBoost™, Leg Mounting, 5-Wash Cycle, Stainless Steel`

### Formula 4: LONG_DESC1 (Comprehensive Technical Narrative)
- **Formula:** `<BRAND_NAME> <PRODUCT_NAME> <WITH>, <SERIES>, <SPECS_LIST>, Additional Information: <EXTRA_SPECS>`
- **Output:** `FRIGIDAIRE® Dishwasher With CleanBoost™, Professional Series, 5 Wash Cycles, 120 V, 15 A, Leg Mounting, 24 in W x 24-1/4 in D, 50-1/4 in Depth With Door Open, 8-1/2 in Upper Rack, 11-1/4 in Lower Rack Minimum Height, 10-3/8 in Upper Rack, 13-1/4 in Lower Rack Maximum Height, 47 dBA Sound Level, Stainless Steel, Additional Information: 240 kW-hr Annual Energy, 1 to 12 hr Delay Start Hours`

### Formula 5: RETAIL_DESC & MARKETING_DESCRIPTION
- **RETAIL_DESC:** `Professional Series Dishwasher, Leg Mounting, 5-Wash Cycle, Stainless Steel`
- **MARKETING_DESCRIPTION:** `Load more and run less with our quietest and largest capacity dishwasher. A 3rd Rack provides dedicated space for mugs and bowls, while an adjustable 2nd Rack helps fit all the dishes and pans your family piles up.`

---

## 4. Output Schema & 252-Column Target Mapping

| 252-Column Field | Value Example |
| :--- | :--- |
| `INVOICE_DESC` | `DISHWASHER LEG 5 SST 120V 15A 50-1/4IN` |
| `MOBILE_DESC` | `Rheem Manufacturing FRIGIDAIRE, Dishwasher, Professional Series, PDSH4816AF` |
| `SHORT_DESC` | `FRIGIDAIRE® Professional Series PDSH4816AF Dishwasher With CleanBoost™, Leg Mounting, 5-Wash Cycle, Stainless Steel` |
| `LONG_DESC1` | `FRIGIDAIRE® Dishwasher With CleanBoost™, Professional Series, 5 Wash Cycles, 120 V, 15 A, Leg Mounting, 24 in W x 24-1/4 in D, 50-1/4 in Depth With Door Open, 8-1/2 in Upper Rack, 11-1/4 in Lower Rack Minimum Height, 10-3/8 in Upper Rack, 13-1/4 in Lower Rack Maximum Height, 47 dBA Sound Level, Stainless Steel, Additional Information: 240 kW-hr Annual Energy, 1 to 12 hr Delay Start Hours` |
| `RETAIL_DESC` | `Professional Series Dishwasher, Leg Mounting, 5-Wash Cycle, Stainless Steel` |
| `ITEM_FEATURES_1` | `3rd rack with extra wash action` |
| `ITEM_FEATURES_2` | `Adjustable 2nd Rack` |
| `ITEM_FEATURES_3` | `41 dBA` |
| `ITEM_FEATURES_4` | `Moisture Repellent Silverware Basket` |
| `ITEM_FEATURES_5` | `Sensor cycle` |

---

## 5. Worked Test Cases

### Case 1: Whirlpool Eco Series Dishwasher
- **Invoice Desc:** `DISHWASHER BLTLN SST SST 120V 10A 41DBA` (Length: 39 chars $\le 40$)
- **Mobile Desc:** `Whirlpool, Dishwasher, Eco Series, WDTS7024RZ, Built-in Mounting` (Length: 64 chars $\in [60, 80]$)
- **Short Desc:** `Whirlpool® Eco Series WDTS7024RZ Dishwasher, Built-in Mounting, Stainless Steel, Stainless Steel`

### Case 2: Milwaukee Metal Cut-Off Disc
- **Invoice Desc:** `DISC CUT OFF 4-1/2X.045X7/8 PERF+ 10PK` (Length: 38 chars $\le 40$)
- **Mobile Desc:** `Milwaukee Electric Tool Corporation Milwaukee, Cut-Off Disc, 49-94-0101` (Length: 71 chars $\in [60, 80]$)
- **Short Desc:** `Milwaukee® Performance+ 49-94-0101 4-1/2 in x .045 in x 7/8 in Metal Cut-Off Disc, 10-Pack`
