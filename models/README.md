# 🔬 OmniSpec AI — Modular Offline Model Research & Evaluation Studio

This directory is strictly isolated from the backend runtime to allow independent experimentation, training, statistical calibration, and evaluation of ML models before exporting production parameters to the backend.

Each model family is organized into its own self-contained sub-folder containing its dedicated training dataset generators, training harnesses, evaluation scripts, and exported weights/parameters.

---

## 📁 Modular Directory Structure

```text
models/
├── dpi_risk_model/                  # 🎯 Defect Probability Index & Risk Calibration Model
│   ├── train_dpi_scorer.py          # Scikit-Learn training & isotonic calibration harness
│   ├── evaluate_models.py           # Offline benchmarking (Accuracy, F1, Confusion Matrix, Queue Distribution)
│   ├── dpi_model_weights.json       # Exported calibrated model weights & risk thresholds
│   └── README.md                    # Model documentation & training logs
│
├── compatibility_substitutes/       # 🔧 Mechanical & Electrical Constraint Matrix (Phase 7)
│   └── ...                          # Rules & domain matrices for abrasives, tools, plumbing, and lighting
│
├── parametric_ast_compiler/         # 🔮 Planned Phase 8: NL -> SQL/EAV Parametric Filter Compiler
│   └── ...
│
├── variant_family_clusterer/        # 🔮 Planned Phase 9: HDBSCAN / Agglomerative Family Inducer
│   └── ...
│
└── README.md                        # Master ML Directory Overview
```

---

## 🎯 Model Modules Overview

### 1. `dpi_risk_model/` — Defect Probability Index (DPI)
- **Goal**: Predict the probability $P(\text{Defect} = 1)$ for a catalog record based on multi-variate signal vectors.
- **Model**: Logistic Regression with Isotonic Probability Calibration (`scikit-learn`).
- **Input Features**:
  1. `brand_confidence_delta`: $1.0 - \text{Brand Confidence}$
  2. `missing_trademark_symbol`: Binary indicator ($1$ if `®`/`™` missing from brand)
  3. `invoice_desc_overflow`: Character overflow past the 40-character maximum cap
  4. `mobile_desc_bounds_delta`: Deviation outside $[60, 80]$ characters
  5. `integrity_violations_count`: Number of failed integrity checks
  6. `sourcing_confidence_delta`: $1.0 - \text{Sourcing Confidence}$
  7. `unverified_mfr_url`: Binary flag ($1$ if URL is missing or non-whitelisted)
- **Performance**:
  - **Accuracy**: $99.53\%$
  - **F1 Score**: $0.9930$
  - **False Positive Rate**: $0.0\%$
- **Export Artifact**: `dpi_model_weights.json` $\rightarrow$ integrated into `backend/app/services/defect_risk_scorer.py`.

---

## 🚀 How to Run Model Experiments

### Train DPI Model:
```powershell
.venv\Scripts\python models/dpi_risk_model/train_dpi_scorer.py
```

### Evaluate DPI Model:
```powershell
.venv\Scripts\python -m models.dpi_risk_model.evaluate_models
```
