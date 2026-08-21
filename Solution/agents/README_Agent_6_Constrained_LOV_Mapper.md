# 🗄️ Agent 6: Constrained LOV Value Mapper & Knowledge Graph Agent
### *OmniSpec AI — 161,000-Row UniCat LOV & Category-Specific Schema Binding Engine*

---

## 1. Architectural Blueprint & Component Topology

```mermaid
flowchart TD
    subgraph LOV_INPUT ["📥 Extracted Specs & Category Context"]
        A3_CP["Classpath & Active Category Schema (from Agent 3)"]
        A4_SPECS["Extracted Specs, Dims & Electricals (from Agent 4)"]
        A5_OEM["OEM Grounded Specs & Approvals (from Agent 5)"]
    end

    subgraph AGENT_6_CORE ["⚙️ Agent 6 LOV Binding Engine (ConstrainedLOVMapperAgent)"]
        direction TB
        STEP1["1. Schema Attribute Sequence Loader<br/>• Queries DuckDB Unicat_Lov table (161K rows)<br/>• Identifies ordered attribute slots for active Classpath"]
        STEP2["2. Many-to-One Canonical Synonym Normalizer<br/>• Maps raw supplier strings to controlled LOV values<br/>• e.g., 'Stainless', 'SS', 'Inox' → 'Stainless Steel'"]
        STEP3["3. 50-Triple Structured Grid Allocator (150 Columns)<br/>• Generates ATTRIBUTE_LABEL 1..50<br/>• Generates ATTRIBUTE_VALUE 1..50<br/>• Generates ATTRIBUTE_UOM 1..50"]
        STEP4["4. Deep Category Rule Enforcer<br/>• Faucets: Mounting, Flow Rate, Spout Height<br/>• Fittings: Fitting Type, Connection Types, Material Construction<br/>• Power Tools: Voltage, Battery Platform, Chuck Size"]
        
        STEP1 --> STEP2 --> STEP3 --> STEP4
    end

    subgraph LOV_OUTPUT ["📦 State Delta Output (ProductEnrichmentState)"]
        TRIPLES["attributes: {'ATTRIBUTE_LABEL 1': 'Sound Level', 'ATTRIBUTE_VALUE 1': '42 dBA', ...}"]
        COUNT["mapped_attributes_count: 4 slots bound, 46 padded empty slots"]
    end

    LOV_INPUT --> STEP1
    STEP4 --> LOV_OUTPUT
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Description / Example |
| :--- | :--- | :--- |
| `Classpath` | Agent 3 | `Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers` |
| `raw_specs_dict` | Agent 4/5 | `{"Sound Level": "42", "Sound Level UOM": "dBA", "Mounting": "Leg", ...}` |
| `BRAND_NAME` | Agent 2 | `Bosch®` |

---

## 3. The 150-Column EAV Triple Structure (50 Triples)

The delivery format requires exactly 50 attribute triples (150 columns) formatted as:
```text
ATTRIBUTE_LABEL 1  | ATTRIBUTE_VALUE 1  | ATTRIBUTE_UOM 1
ATTRIBUTE_LABEL 2  | ATTRIBUTE_VALUE 2  | ATTRIBUTE_UOM 2
...
ATTRIBUTE_LABEL 50 | ATTRIBUTE_VALUE 50 | ATTRIBUTE_UOM 50
```

### Triples Allocation Example:
```json
{
  "ATTRIBUTE_LABEL 1": "Sound Level",
  "ATTRIBUTE_VALUE 1": "42",
  "ATTRIBUTE_UOM 1": "dBA",
  "ATTRIBUTE_LABEL 2": "Selling Qty",
  "ATTRIBUTE_VALUE 2": "1",
  "ATTRIBUTE_UOM 2": "Each",
  "ATTRIBUTE_LABEL 3": "Standard Packaging Information",
  "ATTRIBUTE_VALUE 3": "1 Each",
  "ATTRIBUTE_UOM 3": ""
}
```

---

## 4. Execution Telemetry & Performance
- **Average Latency:** $1.0\text{--}3.5\text{ ms}$ per SKU.
- **Trace Output:** Logs `[Agent 6 ✓] LOV Schema Attributes Bound (<ms> ms)`.
