# 🌐 Agent 5: Autonomous OEM Sourcing & Spec Sheet RAG Agent
### *OmniSpec AI — Sourcing-Hierarchy-Enforced Web & PDF Document Intelligence Engine*

---

## 1. Agent Overview & Role

The **Autonomous OEM Sourcing & Spec Sheet RAG Agent** retrieves authoritative manufacturer technical documents and specification tables from the open web while strictly adhering to the **Unilog Sourcing Hierarchy**. In industrial commerce, aggregator and marketplace data (e.g. Amazon, Grainger, eBay) is frequently inaccurate or unverified; all enriched specifications must originate directly from the original equipment manufacturer (OEM).

### Core Objectives:
1. **Sourcing Hierarchy Compliance:** Discover and link exclusively official OEM manufacturer URLs (`MFR URL`, `Ref URL 1..5`).
2. **Official Technical Document Discovery:** Locate and index official OEM PDF assets (Specification Sheets, Installation Manuals, SDS sheets, Owners Manuals, Submittals, Line Drawings).
3. **Tabular PDF & HTML Spec Extraction:** Parse complex engineering spec tables, electrical schematics, and certification blocks using multimodal Document Intelligence and Vision-Language models.
4. **Standards & Approvals Aggregation:** Extract multi-value regulatory standards (e.g. `ASSE 1006|CEE Tier 2 Qualified|cUL Listed|ENERGY STAR Certified|NSF Certified|UL Listed`).

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 5 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Resolved Brand & MPN from Agent 2 ]                                                            |
|   • MFR: "Rheem Manufacturing", Brand: "FRIGIDAIRE®", MPN: "PDSH4816AF"                           |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Targeted OEM Query: site:frigidaire.com "PDSH4816AF"                                   │   |
|   │ 2. Sourcing Hierarchy Gatekeeper: Reject marketplace & distributor domains                 │   |
|   │ 3. Fetch Official Product Page ──► Extract MFR URL & Support Documentation Links          │   |
|   │ 4. Download & Parse Specification Sheet PDF (PyMuPDF + Vision LLM)                         │   |
|   │ 5. Structured Table Extraction: [Wash Cycles, Decibels, Voltage, Amps, Certifications]     │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ▼                                                                                      |
|   [ Extracted OEM Specs & Verified Document URLs ] ───► Handed off to Agent 6 & Agent 8           |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Description / Example |
| :--- | :--- | :--- |
| `MANUFACTURER_NAME` | Agent 2 | `Rheem Manufacturing` |
| `BRAND_NAME` | Agent 2 | `FRIGIDAIRE®` |
| `MANUFACTURER_PART_NUMBER`| Agent 2 | `PDSH4816AF` |
| `Classpath` | Agent 3 | `Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers` |

---

## 3. Strict Sourcing Hierarchy Governance

As mandated by Unilog Internal Content Guidelines, the sourcing hierarchy is strictly enforced:

```
[Tier 1: Approved - OEM Official Website] (e.g. frigidaire.com, milwaukeetool.com, 3m.com, trex.com)
  └── [Tier 2: Approved - Official OEM Specification PDF / Product Data Sheet (PDS)]
        └── [Tier 3: Approved - Official OEM Owner / Installation Manual]
              └── [TIER 4: REJECTED & BANNED - Distributor / Marketplace Sites]
                  (e.g. amazon.com, grainger.com, homedepot.com, supplyhouse.com, ebay.com)
```

### Domain Whitelist / Blacklist Engine:
```python
DISALLOWED_DOMAINS = [
    "amazon.com", "ebay.com", "homedepot.com", "lowes.com", 
    "grainger.com", "mcmaster.com", "zoro.com", "supplyhouse.com",
    "walmart.com", "aliexpress.com", "alibaba.com"
]
```

---

## 4. Detailed Processing Logic & Algorithms

```
+----------------------------------------------------------------------------------------------------+
|                               AUTONOMOUS OEM RETRIEVAL PIPELINE                                    |
+----------------------------------------------------------------------------------------------------+
|  [MFR + MPN] ──► [ Playwright Headless Browser ] ──► [ Official URL Discovery ]                    |
|                                                                 │                                  |
|                                                   ┌─────────────┴─────────────┐                    |
|                                                   ▼                           ▼                    |
|                                         [ HTML Spec Parser ]        [ PDF Spec Sheet Downloader ]  |
|                                                   │                           │                    |
|                                                   │                 [ PyMuPDF / Vision RAG ]       |
|                                                   │                           │                    |
|                                                   └─────────────┬─────────────┘                    |
|                                                                 ▼                                  |
|                                           [ JSON Structured Specs & Document URLs ]                |
+----------------------------------------------------------------------------------------------------+
```

### Step 1: Headless OEM Search & Discovery
The agent executes targeted URL discovery using the canonical brand domain:
- Query: `https://www.frigidaire.com/en/p/owner-center/product-support/PDSH4816AF`
- Or: `https://learnwhirlpool.com/smartsearchresults?searchtext=WDTS7024R`

### Step 2: PDF Document Classification
The agent crawls the OEM page for technical document links and classifies them into delivery target columns:
- If document title contains `"Specification"` or `"Spec Sheet"` $\rightarrow$ `Specification Sheet`
- If title contains `"Installation"` or `"Instructions"` $\rightarrow$ `Instruction/Installation Manual`
- If title contains `"Owner's Manual"` or `"User Guide"` $\rightarrow$ `Owners/User Manual`
- If title contains `"SDS"` or `"Safety Data Sheet"` $\rightarrow$ `SDS` / `SDS_1`
- If title contains `"Energy Star"` $\rightarrow$ `Energy Star Guide`

### Step 3: Multimodal PDF Spec Table Extraction
Using PyMuPDF and Vision-Language models, the agent extracts tabular specifications:
```json
{
  "electrical": {
    "voltage": "120",
    "amperage": "15",
    "annual_energy_kwh": "240"
  },
  "performance": {
    "sound_level_dba": "47",
    "wash_cycles": "5",
    "delay_start_hours": "1 to 12"
  },
  "certifications": [
    "ASSE 1006",
    "CEE Tier 2 Qualified",
    "cUL Listed",
    "ENERGY STAR Certified",
    "NSF Certified",
    "UL Listed"
  ],
  "mounting": "Leg",
  "series": "Professional Series",
  "finish": "Stainless Steel"
}
```

---

## 5. Output Schema & Target Column Mapping

| Target 252-Column Field | Value Generated (Ground Truth Aligned) |
| :--- | :--- |
| `MFR URL` | `https://www.frigidaire.com/en/p/owner-center/product-support/PDSH4816AF` |
| `Ref URL 1` | `https://www.frigidaire.com/en/p/kitchen/dishwashers/built-in-dishwashers/PDSH4816AF` |
| `Standard/Approvals` | `ASSE 1006\|CEE Tier 2 Qualified\|cUL Listed\|ENERGY STAR Certified\|NSF Certified\|UL Listed` |
| `Specification Sheet`| `FRIGIDAIRE_PDSH4816AF_Specification_Sheet.pdf` |
| `Instruction/Installation Manual` | `https://www.whirlpool.com/content/dam/global/documents/202406/installation-instructions-w11323304-revG.pdf` |
| `Owners/User Manual` | `https://www.whirlpool.com/content/dam/global/documents/202412/owners-manual-w11323304-revj.pdf` |
| `Actual Image (Yes/No)` | `Yes` |

---

## 6. Worked Test Case

### Test Input:
```csv
MANUFACTURER_NAME: Whirlpool Corporation
BRAND_NAME: Whirlpool®
MANUFACTURER_PART_NUMBER: WDTS7024RZ
Classpath: Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers
```

### Agent 5 Execution:
1. **OEM Discovery:** Finds Whirlpool official portal `https://learnwhirlpool.com/smartsearchresults?searchtext=WDTS7024R`.
2. **Document Retrieval:**
   - Owners Manual: `https://www.whirlpool.com/content/dam/global/documents/202412/owners-manual-w11323304-revj.pdf`
   - Installation Instructions: `https://www.whirlpool.com/content/dam/global/documents/202406/installation-instructions-w11323304-revG.pdf`
3. **Spec Table Extraction:**
   - Sound Level: `41 dBA`
   - Voltage: `120 V` | Current: `10 A`
   - Mounting: `Built-in`
   - Special Features: `3rd rack with extra wash action`, `Adjustable 2nd Rack`, `Moisture Repellent Silverware Basket`, `Leak Detection System`, `Triple Wash Spray`
