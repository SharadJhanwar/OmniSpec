# 🔬 Product Family Discovery & Assortment Gap Detector Lab

This module researches and evaluates deterministic MPN series decomposition, multi-axis variant induction, and sequence gap detection for industrial distributor assortments.

---

## 🎯 What Problem This Solves

1. **Flat SKU Fragmentation**: Raw catalogs contain disconnected rows (e.g. `DCG413B`, `DCG413P2`, `DCG413R2`). This engine clusters them under a single **Parent Model Family** (`DEWALT DCG413 Series`) and identifies the variant axes (`Configuration: Bare Tool vs 5.0Ah Kit vs FlexVolt Kit`).
2. **Distributor Assortment Gaps**: Analyzes fractional progressions ($1/8'', 1/4'', 3/8'', 1/2'', 3/4'', 1''$) to detect missing catalog sizes with evidence-backed classification (`CONFIRMED_MANUFACTURER_GAP` vs `POTENTIAL_GAP_DETECTED`).

---

## 🚀 How to Run Benchmarks

```powershell
.venv\Scripts\python models/variant_family_clusterer/test_clustering_benchmarks.py
```
