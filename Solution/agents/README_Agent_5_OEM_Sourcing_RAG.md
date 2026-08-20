# 🌐 Agent 5: Autonomous OEM Sourcing & Spec Sheet RAG Agent
### *OmniSpec AI — Sourcing-Hierarchy-Enforced Web & PDF Document Intelligence Engine*

---

## 1. Agent Overview & Role

The **Autonomous OEM Sourcing & Spec Sheet RAG Agent** retrieves authoritative manufacturer technical documents and specification tables while strictly adhering to the **Unilog Sourcing Hierarchy**. In industrial commerce, aggregator and marketplace data (e.g. Amazon, Grainger, eBay) is frequently inaccurate or unverified; all enriched specifications must originate directly from the original equipment manufacturer (OEM).

### Core Objectives:
1. **Sourcing Hierarchy Compliance:** Discover and link exclusively official OEM manufacturer URLs (`MFR URL`, `Ref URL 1..5`).
2. **Official Technical Document Discovery:** Locate and index official OEM PDF assets (Specification Sheets, Installation Manuals, SDS sheets, Owners Manuals, Submittals, Line Drawings).
3. **Multimodal Vision Spec Sheet RAG:** Ingest uploaded engineering drawing images or PDF spec sheets via `gpt-4o-mini` with Vision (`POST /api/v1/enrich/vision`) to extract physical dimensions, electrical nameplates, and mechanical ratings.
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
|   │ 4. Multimodal Vision RAG: Ingest uploaded PDF / engineering blueprints (gpt-4o-mini Vision)│   |
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
