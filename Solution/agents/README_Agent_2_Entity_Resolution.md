# 🏷️ Agent 2: Brand & Entity Resolution Agent
### *OmniSpec AI — UniCat 27K Master Entity Resolution & Trademark Normalization Engine*

---

## 1. Agent Overview & Role

The **Brand & Entity Resolution Agent** is responsible for establishing the definitive manufacturer, legal brand, and trademark identity for every catalog item. Raw distributor feeds frequently list third-party distributors (e.g., `Jam Industrial Supply LLC (JAMIN)`, `Appliance Dealers Cooperative (APPDE)`, `Parksite (6151)`) in the manufacturer field while omitting the actual brand or using abbreviations (e.g., `Milw`, `3M`, `TREX`).

### Core Objectives:
1. **Active Learning Feedback Pre-Check:** Query the DuckDB `kb_active_overrides` table first. If an approved human reviewer correction exists for the MPN, load the approved canonical entity immediately with 1.0 confidence.
2. **Canonical Manufacturer & Brand Resolution:** Map messy supplier text to exact rows in the **27,000+ UniCat Master Database**.
3. **Distributor vs. OEM Disambiguation:** Identify when `Part_Manuf` is merely a wholesale distributor/co-op, and resolve the true OEM manufacturer and brand from description tokens and MPN patterns.
4. **Legal Casing & Trademark Governance:** Instate strict legal casing, entity suffixes (`Inc`, `LLC`, `Corp`), and mandatory intellectual property symbols (`®`, `™`) as required by Unilog Content Guidelines.
5. **OpenAI Generative Fallback & Latency Tracking:** When confidence is $<75\%$ on novel uncataloged brands, invoke OpenAI `gpt-4o-mini` and log explicit API latency badges (`⚡ OpenAI API: XXX ms`).

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
|   │ 0. Active Overrides Store: Check kb_active_overrides table for existing human approval     │   |
|   │ 1. Supplier Disambiguation: Check if supplier is distributor or OEM                        │   |
|   │ 2. Brand Keyword Resolution: "Milw" ──► "Milwaukee"                                        │   |
|   │ 3. RapidFuzz C++ Matching against UniCat 27,000+ Table:                                    │   |
|   │    - Match: MANUFACTURER_NAME = "Milwaukee Electric Tool Corporation"                      │   |
|   │    - Match: BRAND_NAME = "Milwaukee®"                                                      │   |
|   │ 4. Symbol Injection: Ensure mandatory ® / ™ registered marks                               │   |
|   │ 5. Generative Fallback: If score < 85%, route to OpenAI and log API latency badge         │   |
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

The agent indexes the master **`UniCat_Manufacturer_and_Brand_List.xlsx`** (27,000+ rows) and **`kb_active_overrides`**:
- `MANUFACTURER_NAME`: Official legal entity name (e.g. `Milwaukee Electric Tool Corporation`, `Rheem Manufacturing`, `Whirlpool Corporation`, `Freud Inc`, `Stanley Black & Decker Inc`, `Signify North America Corporation`).
- `MANUFACTURER_CODE`: Standardized MFR code (e.g. `MILW`, `RHEEM`, `WHIRL`, `SBD`, `PHIL`).
- `BRAND_NAME`: Controlled brand name with legal symbol (e.g. `Milwaukee®`, `FRIGIDAIRE®`, `Whirlpool®`, `Diablo®`, `3M™`, `TimberTech®`, `Trex®`, `DEWALT®`, `Philips®`).
- `BRAND_CODE`: Unique brand identifier.
