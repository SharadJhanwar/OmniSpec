import sys
import json
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    precision_recall_curve,
    roc_curve,
    confusion_matrix,
    f1_score,
    accuracy_score
)

# Robust import handling whether run as module or script
try:
    from .train_dpi_scorer import generate_training_dataset
except ImportError:
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))
    from train_dpi_scorer import generate_training_dataset


def evaluate_offline_model():
    weights_path = Path(__file__).resolve().parent / "dpi_model_weights.json"
    if not weights_path.exists():
        print("[ERROR] dpi_model_weights.json not found! Run train_dpi_scorer.py first.")
        return

    with open(weights_path, "r", encoding="utf-8") as f:
        model_meta = json.load(f)

    print("=" * 60)
    print("[EVALUATION] OFFLINE MODEL BENCHMARK & CALIBRATION HARNESS")
    print(f"Model: {model_meta['model_type']}")
    print("=" * 60)

    X, y = generate_training_dataset(seed=999) # Separate evaluation seed
    weights = np.array([model_meta["feature_weights"][f] for f in model_meta["feature_names"]])
    intercept = model_meta["intercept"]

    # Compute predicted logits & probabilities using calibrated weights
    logits = np.dot(X, weights) + intercept
    probs = 1.0 / (1.0 + np.exp(-logits))

    # Evaluate against thresholds
    preds = (probs >= 0.5).astype(int)
    cm = confusion_matrix(y, preds)
    acc = accuracy_score(y, preds)
    f1 = f1_score(y, preds)

    print(f"\n[METRICS] Evaluation on {len(X)} Test Samples:")
    print(f"  * Overall Accuracy : {acc * 100:.2f}%")
    print(f"  * F1 Score (Defect): {f1:.4f}")
    print(f"  * True Negatives   : {cm[0, 0]} (Clean correctly auto-approved)")
    print(f"  * False Positives  : {cm[0, 1]} (Clean falsely flagged)")
    print(f"  * False Negatives  : {cm[1, 0]} (Defect missed)")
    print(f"  * True Positives   : {cm[1, 1]} (Defect correctly caught for HITL)")

    # Risk Tier Distribution
    low_thresh = model_meta["risk_thresholds"]["low_risk_max"]
    crit_thresh = model_meta["risk_thresholds"]["critical_risk_min"]

    low_tier_count = int(np.sum(probs < low_thresh))
    elevated_tier_count = int(np.sum((probs >= low_thresh) & (probs < crit_thresh)))
    critical_tier_count = int(np.sum(probs >= crit_thresh))

    print(f"\n[DISTRIBUTION] Review Queue Distribution:")
    print(f"  * LOW RISK (Auto-Approve)        : {low_tier_count} ({low_tier_count/len(X)*100:.1f}%)")
    print(f"  * ELEVATED RISK (Audit)          : {elevated_tier_count} ({elevated_tier_count/len(X)*100:.1f}%)")
    print(f"  * CRITICAL RISK (Immediate HITL) : {critical_tier_count} ({critical_tier_count/len(X)*100:.1f}%)")
    print("=" * 60)


if __name__ == "__main__":
    evaluate_offline_model()
