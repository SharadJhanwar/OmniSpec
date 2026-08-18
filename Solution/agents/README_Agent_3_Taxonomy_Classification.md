# 🌲 Agent 3: Taxonomy, UNSPSC & Classpath Classifier Agent
### *OmniSpec AI — Hierarchical Category Mapping & UNSPSC Classification Engine*

---

## 1. Agent Overview & Role

The **Taxonomy, UNSPSC & Classpath Classifier Agent** establishes the hierarchical product categorization according to the UniCat taxonomy. Proper classification is the critical prerequisite for attribute enrichment: in the Unilog standard, **every Classpath dictates which specific attributes apply, which are filterable, and the permitted List of Values (LOV)**.

### Core Objectives:
1. **Hierarchical Classpath Prediction:** Classify each product into the exact 3-to-4 tier taxonomy path (e.g. `Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers`).
2. **UNSPSC Code Assignment:** Assign the standard 8-digit United Nations Standard Products and Services Code (UNSPSC).
3. **Internal ERP Classification:** Populate legacy classification levels: `Dept`, `Class`, and `Fine`.
4. **Product Name Standardization:** Extract the canonical base item noun phrase (e.g., `Dishwasher`, `Metal Cut-Off Disc`, `Sanding Belt`, `Decking Board`, `Fascia Board`).
5. **Dynamic LOV Schema Activation:** Dynamically load the exact attribute schema and allowed value constraints required by Agent 6.

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 3 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Cleaned Product Tokens from Agent 1 & Resolved Brand from Agent 2 ]                            |
|   • Brand: "FRIGIDAIRE®"                                                                           |
|   • Desc: "PDSH4816AF Dishwasher SS - Display Only"                                                |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Keyword & Category Feature Extractor ("Dishwasher", "SS", "Built-In")                   │   |
|   │ 2. Hierarchical Category Tree Traversal (DuckDB Taxonomy Trie)                             │   |
|   │ 3. Assign Canonical Classpath:                                                             │   |
|   │    "Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers"         │   |
|   │ 4. Assign Dept / Class / Fine: ["Appliances", "Large Appliances", "Dishwashers"]           │   |
|   │ 5. Map UNSPSC Code: 52141505                                                               │   |
|   │ 6. Extract Canonical Product Name: "Dishwasher"                                            │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ▼                                                                                      |
|   [ Taxonomy Context & Active Category LOV Schema ] ───► Handed off to Agent 5, 6 & 7             |
+----------------------------------------------------------------------------------------------------+
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
              └── [Level 4: Leaf Node / Classpath]
```

### Examples from Ground Truth:

| Dept | Class | Fine | Full Classpath | Canonical Product Name |
| :--- | :--- | :--- | :--- | :--- |
| `Appliances` | `Large Appliances` | `Dishwashers` | `Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers` | `Dishwasher` |
| `Abrasives` | `Cut-Off Wheels` | `Metal Cut-Off`| `Abrasives & Polishing > Cut-Off & Grinding Wheels > Cut-Off Wheels` | `Metal Cut-Off Disc` |
| `Building Materials` | `Decking` | `Composite Decking` | `Building Materials > Decking & Railing > Decking Boards` | `Decking Board` |
| `Plumbing` | `Faucets` | `Kitchen Faucets` | `Plumbing > Commercial & Residential Faucets > Kitchen Sink Faucets` | `Kitchen Sink Faucet` |
| `Plumbing` | `Fittings` | `Pipe Fittings` | `Plumbing > Pipe, Tube & Hose Fittings > Pipe Fittings` | `Pipe Coupling` |

---

## 4. Detailed Classification Logic & Algorithms

```
+----------------------------------------------------------------------------------------------------+
|                             HYBRID DETERMINISTIC + SEMANTIC CLASSIFIER                             |
+----------------------------------------------------------------------------------------------------+
|  Tokens ──► [ Rule-based Category Noun Matcher ] ──► [ RapidFuzz Classpath Match (DuckDB Index) ]   |
|                                                                 │                                  |
|                                                   ┌─────────────┴─────────────┐                    |
|                                                   ▼                           ▼                    |
|                                            [ Match >= 85% ]           [ LLM Semantic Tree Traversal]|
|                                                   │                           │                    |
|                                                   └─────────────┬─────────────┘                    |
|                                                                 ▼                                  |
|                                             [ Ingest UNSPSC & Activate Category LOV ]              |
+----------------------------------------------------------------------------------------------------+
```

### Step 1: Deterministic Category Keyword Matcher
High-frequency industrial categories are matched immediately via token heuristics:
```python
CATEGORY_RULES = {
    "DISHWASHER": {
        "classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
        "dept": "Appliances",
        "class": "Large Appliances",
        "fine": "Dishwashers",
        "product_name": "Dishwasher",
        "unspsc": "52141505"
    },
    "CUT OFF DISC": {
        "classpath": "Abrasives & Polishing>Cut-Off & Grinding Wheels>Cut-Off Wheels",
        "dept": "Abrasives",
        "class": "Abrasive Wheels",
        "fine": "Cut-Off Discs",
        "product_name": "Cut-Off Disc",
        "unspsc": "31191500"
    },
    "DECKING": {
        "classpath": "Building Materials>Decking & Railing>Decking Boards",
        "dept": "Building Materials",
        "class": "Decking",
        "fine": "Decking Boards",
        "product_name": "Decking Board",
        "unspsc": "30103600"
    }
}
```

### Step 2: Semantic Classpath Vector Search
If deterministic rules do not yield an unambiguous match, the agent runs a cosine similarity search against the **161,000-row UniCat Taxonomy Index** using MiniLM embeddings, returning the top-3 candidate leaf nodes.

### Step 3: Leaf Node & UNSPSC Verification
The chosen leaf node is validated to ensure it exists in the active UniCat LOV index. The corresponding 8-digit UNSPSC code is attached.

---

## 5. Output Schema & Target Column Mapping

| Target 252-Column Field | Value Generated |
| :--- | :--- |
| `Classpath` | `Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers` |
| `Dept` | `Appliances` |
| `Class` | `Large Appliances` |
| `Fine` | `Dishwashers` |
| `Product Name` | `Dishwasher` |
| `UNSPSC` | `52141505` |

---

## 6. Worked Test Cases

### Case 1: Trex Composite Decking Row
- **Input:** `Part_Desc: 1nx6-16' Honey Grove Grooved - Trex Enhance Naturals Decking`
- **Classification Execution:**
  - Detect keyword `"Decking"` and brand `"TREX"`.
  - Classpath: `Building Materials>Decking & Railing>Decking Boards`
  - Dept: `Building Materials` | Class: `Decking` | Fine: `Composite Decking Boards`
  - Product Name: `Decking Board`

### Case 2: Diablo Sanding Sponge
- **Input:** `Part_Desc: DFBLBLOMFN01G Diablo 220 Grit - Flat Edge Sanding Sponge`
- **Classification Execution:**
  - Detect keywords `"Sanding Sponge"`, `"Grit"`.
  - Classpath: `Abrasives & Polishing>Sandpaper & Abrasive Pads>Sanding Sponges & Blocks`
  - Product Name: `Sanding Sponge`
