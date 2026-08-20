# 🔬 Parametric Search & Engineering AST Compiler Lab

This module researches and evaluates Natural Language to Parametric Abstract Syntax Tree (AST) compilation for industrial B2B procurement queries.

---

## 🎯 What Problem This Solves

Industrial queries contain hard dimensional, electrical, and mechanical constraints (e.g. `under 45 dBA`, `7/8 in arbor`, `150# NPT`, `2700 K`, `20V cordless`). This module parses complex physical phrasing into structured AST nodes that compile directly to DuckDB SQL queries.

---

## 📐 Formal AST Specification

```json
{
  "raw_query": "Dishwasher under 45 dBA stainless steel 120V 15A",
  "category_intent": "Appliances & Consumer Electronics>Kitchen Appliances>Built-In Dishwashers",
  "numerical_constraints": [
    { "field": "Sound Level", "operator": "<=", "value": 45.0, "unit": "dBA" },
    { "field": "Amperage", "operator": "==", "value": 15.0, "unit": "A" }
  ],
  "categorical_constraints": [
    { "field": "Voltage", "operator": "CONTAINS", "value": "120 V" },
    { "field": "Finish", "operator": "CONTAINS", "value": "Stainless Steel" }
  ],
  "compiled_sql": "SELECT * FROM catalog_delivery_252 WHERE UPPER(Classpath) LIKE '%BUILT-IN DISHWASHERS%' AND TRY_CAST(Sound_Level AS FLOAT) <= 45.0 AND UPPER(Voltage) LIKE '%120 V%' AND UPPER(Finish) LIKE '%STAINLESS STEEL%'",
  "parser_used": "DETERMINISTIC_REGEX",
  "parsing_latency_ms": 0.125
}
```

---

## 🚀 How to Run Benchmarks

```powershell
.venv\Scripts\python models/parametric_search/test_search_benchmarks.py
```
