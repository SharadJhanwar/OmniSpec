# 🗄️ Agent 6: Constrained LOV Value Mapper & Knowledge Graph Agent
### *OmniSpec AI — 161,000-Row UniCat LOV & Category-Specific Schema Binding Engine*

---

## 1. Agent Overview & Role

The **Constrained LOV Value Mapper & Knowledge Graph Agent** is the deterministic guardrail of OmniSpec AI. In industrial e-commerce, free-text LLM generation scores zero if attribute values are hallucinated or deviate from controlled taxonomies. Buyers rely on standardized facet filters to specify exact pipe fittings, electrical ratings, or faucet dimensions.

### Core Objectives:
1. **Zero-Hallucination Schema Binding:** Enforce the **161,000-row UniCat List of Values (LOV)** database. Attribute values must strictly match the normalized values assigned to the active Classpath.
2. **150-Column Dynamic EAV Allocation:** Populate up to 50 structured attribute triples: `[ATTRIBUTE_LABEL i, ATTRIBUTE_VALUE i, ATTRIBUTE_UOM i]`.
3. **Many-to-One Canonical Normalization:** Map thousands of non-standard supplier spellings to canonical controlled values (e.g. collapsing 1,472 fitting connection variants into 515 approved terms).
4. **Deep Category Specialization:** Implement category-specific rule sheets for **Faucets** (mounting, flow rate, spout height) and **Fittings** (fitting type, connection types, material construction).
5. **Special Field Aggregation:** Populate `With`, `Includes`, `Application`, `Prop 65`, and `Warranty` (`1 Year Manufacturer, 1 Year Labor and Parts`).

```
+----------------------------------------------------------------------------------------------------+
|                                      AGENT 6 FLOW DIAGRAM                                          |
|                                                                                                    |
|   [ Extracted Technical Specs from Agent 4 & Agent 5 ]                                             |
|   • Classpath: "Appliances & Consumer Electronics > Kitchen Appliances > Built-In Dishwashers"     |
|   • Raw Specs: { "wash_cycles": "5", "voltage": "120", "amps": "15", "mounting": "Leg" }          |
|             │                                                                                      |
|             ▼                                                                                      |
|   ┌────────────────────────────────────────────────────────────────────────────────────────────┐   |
|   │ 1. Load Active Classpath Schema from UniCat LOV (DuckDB In-Memory Table)                   │   |
|   │ 2. Sequence Attribute Order (1: Series, 2: Model, 3: Number of Wash Cycles, 4: Voltage...) │   |
|   │ 3. Validate & Map Raw Values to Canonical Normalized Values                                │   |
|   │ 4. Many-to-One Synonym Collapse (e.g. "Stainless" ──► "Stainless Steel")                  │   |
|   │ 5. Allocate 50-Triple Structured Grid: [ATTRIBUTE_LABEL i, ATTRIBUTE_VALUE i, UOM i]        │   |
|   │ 6. Format "Additional Information" String for Auxiliary Specs                              │   |
|   └────────────────────────────────────────────────────────────────────────────────────────────┘   |
|             │                                                                                      |
|             ▼                                                                                      |
|   [ 150-Column Structured EAV Grid & Normalized Specs ] ───► Handed off to Agent 7 (Copy Builder)  |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Input Schema & Data Contract

| Field Name | Source | Description / Example |
| :--- | :--- | :--- |
| `Classpath` | Agent 3 | `Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers` |
| `raw_specs_dict` | Agent 4/5 | `{"Sound Level": "47", "Sound Level UOM": "dBA", "Mounting": "Leg", ...}` |
| `BRAND_NAME` | Agent 2 | `FRIGIDAIRE®` |

---

## 3. Knowledge Base & Reference Dependencies

1. **`Unicat_Lov_v1_0_Updated_With_Remarks.xlsx` (161,000+ rows):**
   - `Classpath` | `Leaf Node` | `Filtering Y/N` | `Attribute Label` | `Attribute Values` | `Normalized Label` | `Normalized Values`
2. **`FAUCETS_LOV.xlsx`:**
   - 4 sheets: Summary (UNSPSC), Online Description Build Order, Attribute Detail (sequence, permitted values, synonyms), Visual Style Guide.
3. **`Fittings_LOV.xlsx`:**
   - 390 valid Fitting Types, 1,472 manufacturer connection variants mapped to 515 canonical values, 464 Material Construction values mapped to 113 canonical values.

---

## 4. Deep Category Many-to-One Normalization Logic

```
+----------------------------------------------------------------------------------------------------+
|                                MANY-TO-ONE NORMALIZATION MATRIX                                    |
+----------------------------------------------------------------------------------------------------+
|  RAW SUPPLIER VARIANT STRINGS                       CANONICAL UNICAT NORMALIZED VALUE              |
+----------------------------------------------------+-----------------------------------------------+
|  "SST", "St. Steel", "304 SS", "Stainless"     ──►  "Stainless Steel"                              |
|  "MNPT", "MIP", "Male Pipe Thd", "NPT Male"    ──►  "MNPT"                                         |
|  "FNPT", "FIP", "Female Pipe Thd", "NPT Fem"   ──►  "FNPT"                                         |
|  "Leg Mnt", "Adjustable Legs", "Legs"          ──►  "Leg"                                          |
|  "Built In", "Built-In", "Under-Counter"       ──►  "Built-in"                                     |
+----------------------------------------------------------------------------------------------------+
```

### Attribute Triple Allocation Algorithm:
```python
def map_attributes_to_eav(classpath: str, extracted_specs: dict, lov_db) -> dict:
    # 1. Fetch official sequence order of attributes for this Classpath
    schema_attributes = lov_db.get_attributes_for_classpath(classpath)
    
    eav_output = {}
    attr_idx = 1
    
    for attr in schema_attributes:
        label = attr["Normalized_Label"]
        uom_default = attr["Approved_UOM"]
        
        if label in extracted_specs and attr_idx <= 50:
            val = extracted_specs[label]
            # Validate against allowed LOV values
            canonical_val = lov_db.normalize_value(classpath, label, val)
            
            eav_output[f"ATTRIBUTE_LABEL {attr_idx}"] = label
            eav_output[f"ATTRIBUTE_VALUE {attr_idx}"] = canonical_val
            eav_output[f"ATTRIBUTE_UOM {attr_idx}"] = uom_default if uom_default else ""
            attr_idx += 1
            
    # Pad remaining slots up to 50
    while attr_idx <= 50:
        eav_output[f"ATTRIBUTE_LABEL {attr_idx}"] = ""
        eav_output[f"ATTRIBUTE_VALUE {attr_idx}"] = ""
        eav_output[f"ATTRIBUTE_UOM {attr_idx}"] = ""
        attr_idx += 1
        
    return eav_output
```

---

## 5. 50-Pair Structured Grid Output (Dishwasher Example)

| Slot | `ATTRIBUTE_LABEL` | `ATTRIBUTE_VALUE` | `ATTRIBUTE_UOM` |
| :-: | :--- | :--- | :--- |
| **1** | `Series` | `Professional Series` | `""` |
| **2** | `Model` | `""` | `""` |
| **3** | `Number of Wash Cycles` | `5` | `""` |
| **4** | `Voltage Rating` | `120` | `V` |
| **5** | `Amperage Rating` | `15` | `A` |
| **6** | `Mounting Type` | `Leg` | `""` |
| **7** | `Plug Type` | `""` | `""` |
| **8** | `Size` | `24 in W x 24-1/4 in D` | `""` |
| **9** | `Depth With Door Open` | `50-1/4` | `in` |
| **10** | `Minimum Height` | `8-1/2 in Upper Rack, 11-1/4 in Lower Rack` | `""` |
| **11** | `Maximum Height` | `10-3/8 in Upper Rack, 13-1/4 in Lower Rack` | `""` |
| **12** | `Sound Level` | `47` | `dBA` |
| **13** | `Material` | `Stainless Steel` | `""` |
| **14** | `Color` | `""` | `""` |
| **15** | `Additional Information`| `240 kW-hr Annual Energy, 1 to 12 hr Delay Start Hours` | `""` |

---

## 6. Worked Test Case

### Test Input:
```json
{
  "Classpath": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
  "Extracted": {
    "Series": "Eco Series",
    "Voltage Rating": "120",
    "Amperage Rating": "10",
    "Mounting Type": "Built-in",
    "Size": "33-7/16 in H x 23-7/8 in W x 22-5/8 in D",
    "Depth With Door Open": "50-3/16",
    "Minimum Height": "33-7/16",
    "Sound Level": "41",
    "Material": "Stainless Steel",
    "Color": "Stainless Steel"
  }
}
```

### Agent 6 Execution:
1. **Schema Check:** Verifies all 10 attribute labels exist under `Built-In Dishwashers`.
2. **LOV Normalization:**
   - `Voltage Rating` $\rightarrow$ Value: `120`, UOM: `V`
   - `Amperage Rating` $\rightarrow$ Value: `10`, UOM: `A`
   - `Depth With Door Open` $\rightarrow$ Value: `50-3/16`, UOM: `in`
   - `Sound Level` $\rightarrow$ Value: `41`, UOM: `dBA`
3. **Special Fields:**
   - `With`: `"With Washing 3rd Rack, Water Repellent Silverware Basket"`
   - `Standard/Approvals`: `"ENERGY STAR Certified|UL Listed"`
   - `Warranty`: `"1 Year Manufacturer, 1 Year Labor and Parts"`
