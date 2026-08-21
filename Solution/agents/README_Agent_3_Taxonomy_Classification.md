# 🌲 Agent 3: Taxonomy, UNSPSC & Classpath Classifier Agent
### *OmniSpec AI — Hierarchical Category Mapping & UNSPSC Classification Engine*

---

## 1. Architectural Blueprint & Component Topology

```mermaid
flowchart TD
    subgraph TAXONOMY_INPUT ["📥 Ingestion & Entity Context"]
        A1_TOKENS["Cleaned Description Tokens (from Agent 1)"]
        A2_BRAND["Canonical Brand & Manufacturer (from Agent 2)"]
        A1_SLANG["Thesaurus Classification Hint (if slang detected)"]
    end

    subgraph AGENT_3_CORE ["⚙️ Agent 3 Taxonomy Engine (TaxonomyClassifierAgent)"]
        direction TB
        STEP1["1. Token Keyword & Multi-Gram Matching<br/>• Extracts noun phrases ('Dishwasher', 'Cut-Off Disc', 'Sanding Belt')<br/>• Cross-references Brand Category Priors (e.g. SKF → Bearings)"]
        STEP2["2. 4-Tier Category Graph Traversal<br/>• Traverses DuckDB Category Trie (Dept > Class > Fine > Product)"]
        STEP3["3. Exact Leaf UNSPSC Assignment<br/>• Resolves 8-digit United Nations Standard Code (e.g. 52141505)"]
        STEP4["4. Dynamic LOV Schema Activation<br/>• Retrieves allowed attribute slots from DuckDB LOV dictionary (161K rows)"]
        
        STEP1 --> STEP2 --> STEP3 --> STEP4
    end

    subgraph TAXONOMY_OUTPUT ["📦 State Delta Output (ProductEnrichmentState)"]
        CP["classpath: 'Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers'"]
        DEPT["dept: 'Appliances', class_name: 'Kitchen Appliances', fine: 'Built-In Dishwashers'"]
        PNAME["product_name: 'Dishwasher' (Confidence: 98.0%)"]
        UNSPSC["unspsc: '52141505'"]
        LOV_SCHEMA["active_lov_slots: 4 defined slots"]
    end

    TAXONOMY_INPUT --> STEP1
    STEP4 --> TAXONOMY_OUTPUT
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Example Value |
| :--- | :--- | :--- |
| `clean_mfg_part_num` | Agent 1 | `PDSH4816AF` |
| `cleaned_part_desc` | Agent 1 | `Dishwasher SS - Display Only` |
| `BRAND_NAME` | Agent 2 | `FRIGIDAIRE®` |
| `MANUFACTURER_NAME` | Agent 2 | `Rheem Manufacturing` |
| `extracted_token_bag`| Agent 1 | `{"keywords": ["Dishwasher", "SS", "Sanding Belt", "Cut Off Disc"]}` |

---

## 3. Taxonomy Hierarchy Structure

The UniCat taxonomy organizes products across four standard levels:

```
[Level 1: Dept]
   └── [Level 2: Class]
          └── [Level 3: Fine]
                 └── [Level 4: Product Name / Leaf Commodity]
```

### Major Industrial Taxonomy Mappings

| Product Noun / Raw Keywords | Canonical 4-Tier Classpath | 8-Digit Leaf UNSPSC |
| :--- | :--- | :--- |
| `Dishwasher`, `Built-In SS` | `Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers` | `52141505` |
| `Cut-Off Disc`, `Abrasive Wheel` | `Abrasives > Cut-Off Wheels > Metal Cut-Off Wheels` | `31191506` |
| `Sanding Belt`, `Abrasive Belt` | `Abrasives > Sanding Belts & Discs > Portable Sanding Belts` | `31191501` |
| `Decking Board`, `Grooved Deck` | `Building Materials > Decking & Railing > Composite Decking Boards` | `30151802` |
| `Wire Stripper`, `Wire Cutter` | `Tools & Instruments > Hand Tools > Wire Strippers & Cutters` | `27111514` |
| `Ball Bearing`, `Deep Groove` | `Power Transmission > Bearings & Bushings > Ball Bearings` | `26101500` |

---

## 4. Execution Telemetry & Performance
- **Average Latency:** $1.5\text{--}4.0\text{ ms}$ per SKU.
- **Trace Output:** Logs `[Agent 3 ✓] Taxonomy Assigned: '<classpath>' [UNSPSC: <unspsc>] (<ms> ms)`.
