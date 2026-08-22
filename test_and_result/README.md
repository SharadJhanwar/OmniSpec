# 🧪 Test & Evaluation Suite

This folder contains the verification test dataset, automated execution runner, and delivery outputs produced by the **OmniSpec AI 10-Agent Swarm**.

---

## 📁 Files in this Folder

| File | Description |
| :--- | :--- |
| [`test.csv`](test.csv) | Raw input dataset containing raw product rows with missing brand and unstructured descriptions. |
| [`generate_output_for_test.py`](generate_output_for_test.py) | Standalone Python pipeline runner that seeds the DuckDB Master KB, executes the 10-Agent Swarm, and generates 252-column delivery files. |
| [`output.csv`](output.csv) | Final 252-Column delivery CSV strictly conforming to the Unilog standard (zero internal metadata fields). |
| [`output.xlsx`](output.xlsx) | Formatted Excel delivery workbook. |
| [`output.json`](output.json) | Complete JSON export containing full attribute mappings, 5-Pillar confidence scores, and agent execution traces. |

---

## 🚀 How to Run

From the repository root:

```powershell
.venv\Scripts\python.exe test_and_result\generate_output_for_test.py
```

Or from inside `test_and_result/`:

```powershell
..\.venv\Scripts\python.exe generate_output_for_test.py
```
