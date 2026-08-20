import os
import json
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, brier_score_loss, classification_report


def generate_training_dataset(seed: int = 42) -> tuple:
    """
    Generates a realistic multi-variate feature dataset based on 
    ground-truth clean records (Defect=0) and corrupted edge-case rows (Defect=1).
    """
    np.random.seed(seed)
    n_clean = 1000
    n_corrupt = 500

    # Clean records (Defect = 0)
    X_clean = np.column_stack([
        np.random.beta(1, 20, size=n_clean) * 0.1,         # brand_conf_delta (~0.0 to 0.05)
        np.zeros(n_clean),                                 # missing_trademark_symbol (0)
        np.zeros(n_clean),                                 # invoice_desc_overflow (0)
        np.random.choice([0, 1, 2], size=n_clean, p=[0.9, 0.08, 0.02]), # mobile_bounds_delta
        np.zeros(n_clean),                                 # integrity_violations (0)
        np.random.beta(1, 20, size=n_clean) * 0.1,         # sourcing_conf_delta (~0.0)
        np.zeros(n_clean)                                  # unverified_mfr_url (0)
    ])
    y_clean = np.zeros(n_clean)

    # Corrupted / High-defect records (Defect = 1)
    X_corrupt = np.column_stack([
        np.random.uniform(0.15, 0.70, size=n_corrupt),     # brand_conf_delta (high uncertainty)
        np.random.choice([0, 1], size=n_corrupt, p=[0.2, 0.8]), # missing trademark symbol
        np.random.exponential(scale=8.0, size=n_corrupt) * np.random.choice([0, 1], size=n_corrupt, p=[0.3, 0.7]), # invoice overflow chars
        np.random.exponential(scale=15.0, size=n_corrupt) * np.random.choice([0, 1], size=n_corrupt, p=[0.2, 0.8]), # mobile bounds delta
        np.random.choice([0, 1, 2, 3], size=n_corrupt, p=[0.1, 0.4, 0.3, 0.2]), # integrity violations
        np.random.uniform(0.20, 0.90, size=n_corrupt),     # sourcing_conf_delta
        np.random.choice([0, 1], size=n_corrupt, p=[0.3, 0.7])  # unverified mfr url
    ])
    y_corrupt = np.ones(n_corrupt)

    X = np.vstack([X_clean, X_corrupt])
    y = np.concatenate([y_clean, y_corrupt])
    return X, y


def train_and_export():
    feature_names = [
        "brand_confidence_delta",
        "missing_trademark_symbol",
        "invoice_desc_overflow",
        "mobile_desc_bounds_delta",
        "integrity_violations_count",
        "sourcing_confidence_delta",
        "unverified_mfr_url"
    ]

    print("=" * 60)
    print("[TRAINING] DEFECT PROBABILITY INDEX (DPI) MODEL")
    print("=" * 60)

    X, y = generate_training_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

    print(f"Total Samples: {len(X)} | Train: {len(X_train)} | Test: {len(X_test)}")

    # 1. Base Logistic Regression Model
    base_clf = LogisticRegression(C=1.0, solver="lbfgs", max_iter=200, random_state=42)
    base_clf.fit(X_train, y_train)

    # 2. Isotonic Probability Calibration
    calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method="isotonic", cv=3)
    calibrated_clf.fit(X_train, y_train)

    # 3. Evaluate Performance
    y_pred_proba = calibrated_clf.predict_proba(X_test)[:, 1]
    y_pred_binary = (y_pred_proba >= 0.5).astype(int)

    auc = roc_auc_score(y_test, y_pred_proba)
    brier = brier_score_loss(y_test, y_pred_proba)

    print(f"\n[EVALUATION] Test Metrics:")
    print(f"  * ROC-AUC Score: {auc:.4f}")
    print(f"  * Brier Calibration Loss: {brier:.4f}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred_binary, target_names=["Clean (0)", "Defect (1)"]))

    # Extract Learned Weights & Intercept
    weights = base_clf.coef_[0]
    intercept = float(base_clf.intercept_[0])

    print("[WEIGHTS] Learned Feature Weights:")
    weights_dict = {}
    for feat, w in zip(feature_names, weights):
        weights_dict[feat] = round(float(w), 4)
        print(f"  * {feat:<30}: {w:+.4f}")

    # Export configuration artifact
    export_payload = {
        "model_type": "LogisticRegression + IsotonicCalibration",
        "feature_names": feature_names,
        "intercept": round(intercept, 4),
        "feature_weights": weights_dict,
        "risk_thresholds": {
            "low_risk_max": 0.25,
            "elevated_risk_max": 0.55,
            "critical_risk_min": 0.55
        },
        "recommended_actions": {
            "LOW": "AUTO_APPROVE",
            "ELEVATED": "SECONDARY_AUDIT",
            "CRITICAL": "IMMEDIATE_HITL_REQUIRED"
        },
        "evaluation_metrics": {
            "roc_auc": round(auc, 4),
            "brier_score": round(brier, 4)
        }
    }

    output_path = Path(__file__).resolve().parent / "dpi_model_weights.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2)

    print(f"\n[SUCCESS] Calibrated weights successfully exported to: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    train_and_export()
