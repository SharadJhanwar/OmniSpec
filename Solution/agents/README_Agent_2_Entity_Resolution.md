# 🏷️ Agent 2: Brand & Entity Resolution Agent
### *OmniSpec AI — UniCat 27K Master Entity Resolution, Active Overrides & Live Evidence Discovery*

---

## 1. Agent Overview & Role

The **Brand & Entity Resolution Agent** is responsible for establishing the definitive manufacturer, legal brand, and trademark identity for every catalog item. Raw distributor feeds frequently list third-party distributors (e.g., `Jam Industrial Supply LLC (JAMIN)`, `Appliance Dealers Cooperative (APPDE)`, `Parksite (6151)`) in the manufacturer field while omitting the actual brand or using abbreviations (e.g., `Milw`, `3M`, `TREX`).

### Core Objectives:
1. **Active Learning Feedback Pre-Check:** Query the DuckDB `kb_active_overrides` table first. If an approved human reviewer correction exists for the MPN, load the approved canonical entity immediately with **1.0 confidence** and mark `is_cached = True`.
2. **Canonical Manufacturer & Brand Resolution:** Map supplier text to exact rows in the **27,000+ UniCat Master Database** (`MANUFACTURER_NAME`, `BRAND_NAME`).
3. **Live Web Search & Evidence Discovery:** When an SKU is uncataloged or ambiguous ($< 75\%$ confidence), query DuckDuckGo via `EvidenceDiscoveryService` to retrieve live product titles and manufacturer snippets.
4. **Evidence-Backed LLM Disambiguation:** Prompt `gpt-4o-mini` with both raw supplier tokens AND live web snippets to discover the true legal OEM identity without hallucinating.
5. **Legal Casing & Trademark Governance:** Instate strict legal casing, entity suffixes (`Inc`, `LLC`, `Corp`), and mandatory intellectual property symbols (`®`, `™`) as required by Unilog Content Guidelines.

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
|   │    └── If found: is_cached=True, conf=1.00 (Bypasses HITL)                                 │   |
|   │ 1. Supplier Disambiguation: Check if supplier is distributor or OEM                        │   |
|   │ 2. Brand Keyword Resolution: "Milw" ──► "Milwaukee"                                        │   |
|   │ 3. RapidFuzz C++ Matching against UniCat 27,000+ Table:                                    │   |
|   │    - Match: MANUFACTURER_NAME = "Milwaukee Electric Tool Corporation"                      │   |
|   │    - Match: BRAND_NAME = "Milwaukee®"                                                      │   |
|   │ 4. Live Evidence Discovery: If conf < 75%, search DuckDuckGo for live OEM snippets        │   |
|   │ 5. Generative LLM Disambiguation: Disambiguate true OEM brand from search evidence         │   |
|   │ 6. Symbol Injection: Ensure mandatory ® / ™ registered marks                               │   |
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
- `MANUFACTURER_NAME`: Official legal entity name (e.g. `Milwaukee Electric Tool Corporation`, `BSH Home Appliances Corporation`, `SKF USA Inc.`, `The Gorman-Rupp Company`).
- `BRAND_NAME`: Canonical brand name with registered marks (e.g. `Milwaukee®`, `Bosch®`, `SKF®`, `Gorman-Rupp®`).
- `TRADE_NAME`: Canonical trade sub-brand (e.g. `Cubitron™ II`, `Diablo®`, `Steel Demon`, `Abranet®`).

---

## 4. Execution Tracing
Emits real-time execution logs and an `AgentTrace` containing:
- `Resolved Brand`: `<BrandName>` (`<ManufacturerName>`)
- `Score`: $0.0\text{--}100.0\%$
- `OpenAI Disambiguated`: `True` / `False` (`<ms> ms`)
- `Live Web Snippets`: Summary of search evidence consulted.
