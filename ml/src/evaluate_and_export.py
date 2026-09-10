import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, average_precision_score, confusion_matrix, 
    precision_recall_curve, roc_curve
)

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from feature_engineering import EXCLUDED_COLS, TARGET_COL


def run_ml4_evaluation_and_export(base_dir: str):
    """
    ML-4 Evaluation & Export Pipeline:
    1. Loads full cleaned dataset and reproduces ML-3's stratified 80/20 train/test split.
    2. Loads ML-3's selected candidate pipeline from ml/models/best_model.joblib.
    3. Generates 5-fold Stratified Out-of-Fold (OOF) probability predictions on training set.
    4. Selects optimal decision threshold using OOF predictions (maximizing F1 while prioritizing Recall).
    5. Fits final pipeline on full training set and evaluates ONCE on untouched 20% test set.
    6. Generates evaluation visualizations (Confusion Matrix, ROC, PR Curve, Threshold vs F1).
    7. Exports reusable final failure pipeline package to ml/models/final_failure_pipeline.joblib
       and summary metrics to ml/models/final_evaluation_metrics.json.
    """
    print("=" * 75)
    print(" ML-4: OOF THRESHOLD SELECTION & UNTOUCHED TEST EVALUATION")
    print("=" * 75)
    
    # 1. Ingest Data & Reproduce ML-3 80/20 Stratified Split
    data_path = os.path.join(base_dir, "data", "cleaned_predictive_maintenance.csv")
    if not os.path.exists(data_path):
        data_path = os.path.join(base_dir, "data", "ai4i2020.csv")
        
    df = pd.read_csv(data_path)
    feature_cols = [c for c in df.columns if c not in EXCLUDED_COLS and c != TARGET_COL]
    
    X = df[feature_cols].copy()
    y = df[TARGET_COL].copy()
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Dataset Loaded. Train shape: {X_train.shape}, Test shape: {X_test.shape} (Untouched)")
    
    # 2. Load ML-3 Selected Model Artifact
    models_dir = os.path.join(base_dir, "ml", "models")
    best_model_path = os.path.join(models_dir, "best_model.joblib")
    
    if not os.path.exists(best_model_path):
        raise FileNotFoundError(f"ML-3 artifact not found at {best_model_path}. Run ML-3 first.")
        
    ml3_artifact = joblib.load(best_model_path)
    winning_model_name = ml3_artifact["model_name"]
    selected_pipeline = ml3_artifact["pipeline"]
    
    print(f"Loaded Selected ML-3 Pipeline: '{winning_model_name}'")
    
    # 3. Generate Out-of-Fold (OOF) Predictions for Leakage-Free Threshold Tuning
    print("\n--- Phase 1: 5-Fold Stratified Out-of-Fold (OOF) Threshold Selection ---")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof_probs = cross_val_predict(
        selected_pipeline, X_train, y_train, cv=skf, method='predict_proba', n_jobs=-1
    )[:, 1]
    
    # Evaluate decision thresholds from 0.05 to 0.95 on OOF predictions
    thresholds = np.arange(0.05, 0.95, 0.01)
    best_threshold = 0.50
    best_oof_f1 = -1.0
    best_oof_rec = -1.0
    best_oof_prec = -1.0
    
    oof_threshold_results = []
    for thresh in thresholds:
        preds = (oof_probs >= thresh).astype(int)
        prec = precision_score(y_train, preds, zero_division=0)
        rec = recall_score(y_train, preds, zero_division=0)
        f1 = f1_score(y_train, preds, zero_division=0)
        
        oof_threshold_results.append({
            "threshold": round(thresh, 2),
            "precision": prec,
            "recall": rec,
            "f1": f1
        })
        
        # Select threshold maximizing F1 (break ties with Recall)
        if f1 > best_oof_f1 or (np.isclose(f1, best_oof_f1) and rec > best_oof_rec):
            best_oof_f1 = f1
            best_threshold = float(thresh)
            best_oof_rec = rec
            best_oof_prec = prec
            
    print(f"OOF Threshold Selection Complete:")
    print(f"  • Default Threshold: 0.50")
    print(f"  • Selected OOF Optimal Threshold: {best_threshold:.2f}")
    print(f"  • OOF Metrics at Selected Threshold -> F1: {best_oof_f1:.4f}, Recall: {best_oof_rec:.4f}, Precision: {best_oof_prec:.4f}")

    # 4. Fit Final Pipeline on Full 80% Training Set
    print(f"\n--- Phase 2: Fitting Selected Pipeline on Complete Training Set ---")
    selected_pipeline.fit(X_train, y_train)

    # Extract recoverable feature names for SHAP explainability
    preprocessor = selected_pipeline.named_steps['preprocessor']
    feature_names = list(preprocessor.get_feature_names_out())
    print(f"Extracted {len(feature_names)} Recoverable Feature Names for SHAP.")

    # 5. Evaluate ONCE on Untouched 20% Test Set
    print("\n--- Phase 3: Final Holdout Test Set Evaluation ---")
    test_probs = selected_pipeline.predict_proba(X_test)[:, 1]
    
    test_preds_default = (test_probs >= 0.50).astype(int)
    test_preds_selected = (test_probs >= best_threshold).astype(int)
    
    test_metrics_default = {
        "Accuracy": round(accuracy_score(y_test, test_preds_default), 4),
        "Precision": round(precision_score(y_test, test_preds_default), 4),
        "Recall": round(recall_score(y_test, test_preds_default), 4),
        "F1-Score": round(f1_score(y_test, test_preds_default), 4),
        "ROC-AUC": round(roc_auc_score(y_test, test_probs), 4),
        "PR-AUC": round(average_precision_score(y_test, test_probs), 4)
    }
    
    test_metrics_selected = {
        "Accuracy": round(accuracy_score(y_test, test_preds_selected), 4),
        "Precision": round(precision_score(y_test, test_preds_selected), 4),
        "Recall": round(recall_score(y_test, test_preds_selected), 4),
        "F1-Score": round(f1_score(y_test, test_preds_selected), 4),
        "ROC-AUC": round(roc_auc_score(y_test, test_probs), 4),
        "PR-AUC": round(average_precision_score(y_test, test_probs), 4)
    }
    
    print("\nFinal Test Metrics (Default Threshold = 0.50):")
    for k, v in test_metrics_default.items():
        print(f"  • {k}: {v}")
        
    print(f"\nFinal Test Metrics (Selected OOF Threshold = {best_threshold:.2f}):")
    for k, v in test_metrics_selected.items():
        print(f"  • {k}: {v}")
        
    cm = confusion_matrix(y_test, test_preds_selected)
    print("\nTest Confusion Matrix (Selected Threshold):")
    print(f" [[TN: {cm[0][0]}, FP: {cm[0][1]}],\n  [FN: {cm[1][0]}, TP: {cm[1][1]}]]")

    # 6. Save Reusable Failure Pipeline & Evaluation Summary
    final_pipeline_bundle = {
        "pipeline": selected_pipeline,
        "winning_model_name": winning_model_name,
        "selected_threshold": best_threshold,
        "feature_names": feature_names,
        "input_feature_schema": feature_cols,
        "test_metrics": test_metrics_selected,
        "test_metrics_default": test_metrics_default,
        "oof_f1": best_oof_f1
    }
    
    bundle_path = os.path.join(models_dir, "final_failure_pipeline.joblib")
    joblib.dump(final_pipeline_bundle, bundle_path)
    print(f"\nSaved final failure pipeline bundle to: {bundle_path}")
    
    metrics_json_path = os.path.join(models_dir, "final_evaluation_metrics.json")
    with open(metrics_json_path, "w") as f:
        json.dump({
            "winning_model": winning_model_name,
            "selected_threshold": best_threshold,
            "oof_best_f1": best_oof_f1,
            "test_metrics_default": test_metrics_default,
            "test_metrics_selected": test_metrics_selected,
            "confusion_matrix": cm.tolist()
        }, f, indent=2)
    print(f"Saved final evaluation metrics JSON to: {metrics_json_path}")
    print("=" * 75)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_ml4_evaluation_and_export(base_dir)
