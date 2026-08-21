# 🌐 Agent 5: Autonomous OEM Sourcing & Spec Sheet RAG Agent
### *OmniSpec AI — Sourcing-Hierarchy-Enforced Web & PDF Document Intelligence Engine*

---

## 1. Architectural Blueprint & Component Topology

```mermaid
flowchart TD
    subgraph SOURCING_INPUT ["📥 Ingestion & Entity State"]
        A2_BRAND["Canonical Brand & MFR (from Agent 2)"]
        A1_MPN["Clean MPN (from Agent 1)"]
        A3_CP["Classpath & Product Noun (from Agent 3)"]
    end

    subgraph AGENT_5_CORE ["⚙️ Agent 5 Sourcing & CRAG Engine (OEMSourcingRAGAgent)"]
        direction TB
        STEP1["1. Multi-Engine OEM Search Discovery<br/>• Uses EvidenceDiscoveryService (DuckDuckGo Search)<br/>• Generates targeted query: '<Brand> <MPN> official datasheet specifications'"]
        STEP2["2. Sourcing Hierarchy Gatekeeper & Blacklist Filter<br/>• BANS marketplaces & retail aggregators (Amazon, eBay, Grainger, Walmart)<br/>• PRIORITIZES direct OEM domains (e.g. skf.com, bosch.com, milwaukeetool.com)"]
        STEP3["3. Corrective RAG (CRAG) Document Evaluator<br/>• Grades retrieved snippets: CORRECT / AMBIGUOUS / INCORRECT<br/>• Scrapes authoritative PDF technical datasheets and submittal cut sheets"]
        STEP4["4. Standards & Approvals Aggregator<br/>• Parses pipe-delimited certifications (ASSE 1006|cUL Listed|ENERGY STAR|UL Listed)"]
        
        STEP1 --> STEP2 --> STEP3 --> STEP4
    end

    subgraph SOURCING_OUTPUT ["📦 State Delta Output (ProductEnrichmentState)"]
        MFR_URL["mfr_url: 'https://www.skf.com/.../productid-W+6205-2RS1'"]
        REF_URLS["ref_url_1: 'https://www.skf.com/datasheet.pdf'"]
        APPROVALS["standard_approvals: 'cUL Listed|ENERGY STAR Certified|UL Listed'"]
        CRAG_GRADE["crag_grade: 'CORRECT'"]
    end

    SOURCING_INPUT --> STEP1
    STEP4 --> SOURCING_OUTPUT
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Description / Example |
| :--- | :--- | :--- |
| `MANUFACTURER_NAME` | Agent 2 | `BSH Home Appliances Corporation` |
| `BRAND_NAME` | Agent 2 | `Bosch®` |
| `MANUFACTURER_PART_NUMBER`| Agent 2 | `SHX78B75UC` |
| `Classpath` | Agent 3 | `Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers` |

---

## 3. Strict Sourcing Hierarchy Governance

As mandated by Unilog Internal Content Guidelines, the sourcing hierarchy is strictly enforced:

```
[Tier 1: Approved - OEM Official Website] (e.g. bosch-home.com, skf.com, milwaukeetool.com, 3m.com)
  └── [Tier 2: Approved - Official OEM Specification PDF / Product Data Sheet (PDS)]
        └── [Tier 3: Approved - Official OEM Owner / Installation Manual]
              └── [TIER 4: REJECTED & BANNED - Distributor / Marketplace Sites (Weight: 0%)]
                  (e.g. amazon.com, grainger.com, homedepot.com, supplyhouse.com, ebay.com)
```

---

## 4. Execution Telemetry & Performance
- **Average Latency:** $1.5\text{--}4.5\text{ s}$ when web search/PDF discovery is invoked; $< 1\text{ ms}$ on local cache hit.
- **Trace Output:** Logs `[Agent 5 ✓] OEM Sourcing URL Grounded: '<mfr_url>' (<ms> ms)`.
