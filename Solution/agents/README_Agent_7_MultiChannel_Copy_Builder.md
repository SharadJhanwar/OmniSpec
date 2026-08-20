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
5. **Retail & Marketing Descriptions:** Produce high-converting marketing overviews with explicit latency tracking (`⚡ OpenAI API: XXX ms`).
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
|   │ 5. Marketing & Retail Copy Builder: High-converting consumer paragraph (OpenAI / Fast-path)│   |
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
| Channel Tier         | Character Target      | Construction Formula / Constraint Rule              |
+----------------------+-----------------------+-----------------------------------------------------+
| 1. INVOICE_DESC      | <= 40 Chars (ALL CAPS)| <ITEM_ABBR> <SPEC_ABBR> <MPN> (e.g. DISHWASHER LEG 5 SST 120V) |
| 2. MOBILE_DESC       | 60 to 80 Chars        | <MFR> <Brand>, <Item>, <Series>, <MPN>, <Key Spec>  |
| 3. SHORT_DESC        | E-Commerce PDP Title  | Brand® + Series + MPN + Item Type + Key Specs       |
| 4. LONG_DESC1        | Exhaustive Spec Copy  | Narrative description + "Additional Information:"   |
| 5. MARKETING_DESC    | High-Converting Copy  | Value proposition paragraph + application context   |
| 6. ITEM_FEATURES_1..20 Benefit Bullets       | Atomic product features and compliance capabilities |
+----------------------+-----------------------+-----------------------------------------------------+
```
