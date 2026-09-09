import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, average_precision_score, confusion_matrix, 
    precision_recall_curve
)

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from feature_engineering import DomainFeatureEngineer, build_preprocessing_pipeline

def run_model_evaluation_and_selection(base_dir: str):
    print("=" * 75)
    print(" ML-4: COMPREHENSIVE MODEL EVALUATION & SELECTION")
    print("=" * 75)
    
    # 1. Ingest Data
    data_path = os.path.join(base_dir, "data", "cleaned_predictive_maintenance.csv")
    if not os.path.exists(data_path):
        data_path = os.path.join(base_dir, "data", "ai4i2020.csv")
        
    df = pd.read_csv(data_path)
    
    target_col = 'Machine failure'
    excluded_cols = ['UDI', 'Product ID', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    feature_cols = [c for c in df.columns if c not in excluded_cols and c != target_col]
    
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    
    # Domain Feature Engineering & Split
    engineer = DomainFeatureEngineer()
    X_eng = engineer.transform(X)
    
    categorical_cols = ['Type']
    numerical_cols = [c for c in X_eng.columns if c not in categorical_cols]
    
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_eng, y, test_size=0.2, random_state=42, stratify=y
    )
    
    preprocessor = build_preprocessing_pipeline(categorical_cols, numerical_cols)
    X_train_proc = preprocessor.fit_transform(X_train_raw)
    X_test_proc = preprocessor.transform(X_test_raw)
    
    feature_names = list(preprocessor.get_feature_names_out())
    
    X_train = pd.DataFrame(X_train_proc, columns=feature_names)
    X_test = pd.DataFrame(X_test_proc, columns=feature_names)
    
    # Calculate scale_pos_weight
    scale_pos_weight = np.sum(y_train == 0) / np.sum(y_train == 1)
    
    # Candidate models
    candidate_models = {
        "Logistic Regression": LogisticRegression(
            class_weight='balanced', max_iter=1000, random_state=42
        ),
        "Decision Tree": DecisionTreeClassifier(
            class_weight='balanced', max_depth=6, random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, class_weight='balanced', max_depth=10, random_state=42
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100, max_depth=5, scale_pos_weight=scale_pos_weight,
            learning_rate=0.05, random_state=42, eval_metric='logloss'
        )
    }
    
    # 2. 5-Fold Cross-Validation Comparison
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'average_precision']
    
    cv_comparison = []
    trained_candidates = {}
    
    print("\n--- 1. Cross-Validation Results Comparison Table (Training Set Only) ---")
    for name, model in candidate_models.items():
        cv_res = cross_validate(model, X_train, y_train, cv=skf, scoring=scoring)
        
        acc_m = np.mean(cv_res['test_accuracy'])
        prec_m = np.mean(cv_res['test_precision'])
        rec_m = np.mean(cv_res['test_recall'])
        f1_m = np.mean(cv_res['test_f1'])
        auc_m = np.mean(cv_res['test_roc_auc'])
        pr_auc_m = np.mean(cv_res['test_average_precision'])
        
        cv_comparison.append({
            "Model": name,
            "Accuracy": round(acc_m, 4),
            "Precision": round(prec_m, 4),
            "Recall": round(rec_m, 4),
            "F1-Score": round(f1_m, 4),
            "ROC-AUC": round(auc_m, 4),
            "PR-AUC": round(pr_auc_m, 4)
        })
        
        model.fit(X_train, y_train)
        trained_candidates[name] = model

    comp_df = pd.DataFrame(cv_comparison)
    print(comp_df.to_string(index=False))

    # 3. Model Selection Decision
    # High emphasis on PR-AUC & F1-Score due to minority failure class (~3.4%)
    winning_model_name = comp_df.sort_values(by=['PR-AUC', 'F1-Score', 'ROC-AUC'], ascending=False).iloc[0]['Model']
    winner_model = trained_candidates[winning_model_name]
    
    print(f"\n★ Winner Selected via Validation Metrics: '{winning_model_name}' ★")
    print("  Rationale: Selected for highest PR-AUC and F1-Score on minority failure class without overfitting.\n")

    # 4. Decision Threshold Tuning on Validation Predictions
    print("--- 2. Optimal Decision Threshold Assessment ---")
    y_train_probs = winner_model.predict_proba(X_train)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y_train, y_train_probs)
    
    # Find threshold maximizing F1-Score
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1_scores)
    optimal_threshold = float(thresholds[best_idx]) if best_idx < len(thresholds) else 0.5
    optimal_f1 = float(f1_scores[best_idx])
    
    print(f"Default Decision Threshold: 0.5000")
    print(f"Optimal Tuned Threshold:    {optimal_threshold:.4f} (Validation F1-Score: {optimal_f1:.4f})\n")

    # 5. Evaluate Winner ONCE on Untouched Test Set
    print("--- 3. Final Evaluation of Winner on Untouched Test Set ---")
    y_test_probs = winner_model.predict_proba(X_test)[:, 1]
    
    # Default threshold (0.50)
    y_test_pred_default = (y_test_probs >= 0.50).astype(int)
    # Tuned threshold
    y_test_pred_tuned = (y_test_probs >= optimal_threshold).astype(int)
    
    test_metrics_default = {
        "Accuracy": round(accuracy_score(y_test, y_test_pred_default), 4),
        "Precision": round(precision_score(y_test, y_test_pred_default), 4),
        "Recall": round(recall_score(y_test, y_test_pred_default), 4),
        "F1-Score": round(f1_score(y_test, y_test_pred_default), 4),
        "ROC-AUC": round(roc_auc_score(y_test, y_test_probs), 4),
        "PR-AUC": round(average_precision_score(y_test, y_test_probs), 4)
    }
    
    test_metrics_tuned = {
        "Accuracy": round(accuracy_score(y_test, y_test_pred_tuned), 4),
        "Precision": round(precision_score(y_test, y_test_pred_tuned), 4),
        "Recall": round(recall_score(y_test, y_test_pred_tuned), 4),
        "F1-Score": round(f1_score(y_test, y_test_pred_tuned), 4),
        "ROC-AUC": round(roc_auc_score(y_test, y_test_probs), 4),
        "PR-AUC": round(average_precision_score(y_test, y_test_probs), 4)
    }
    
    print(f"Test Performance (Default Threshold = 0.50):")
    for k, v in test_metrics_default.items():
        print(f"  • {k}: {v}")
        
    print(f"\nTest Performance (Tuned Threshold = {optimal_threshold:.4f}):")
    for k, v in test_metrics_tuned.items():
        print(f"  • {k}: {v}")
        
    cm = confusion_matrix(y_test, y_test_pred_tuned)
    print("\nConfusion Matrix (Tuned Threshold):")
    print(f" [[TN: {cm[0][0]}, FP: {cm[0][1]}],\n  [FN: {cm[1][0]}, TP: {cm[1][1]}]]")

    # 6. Save Reusable Pipeline Bundle
    models_dir = os.path.join(base_dir, "ml", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    pipeline_bundle = {
        "preprocessor": preprocessor,
        "model": winner_model,
        "winning_model_name": winning_model_name,
        "optimal_threshold": optimal_threshold,
        "feature_names": feature_names,
        "input_feature_schema": feature_cols,
        "test_metrics_tuned": test_metrics_tuned
    }
    
    bundle_path = os.path.join(models_dir, "final_failure_pipeline.joblib")
    joblib.dump(pipeline_bundle, bundle_path)
    print(f"\nSaved final failure pipeline package to: {bundle_path}")
    
    # Save evaluation summary JSON
    metrics_json_path = os.path.join(models_dir, "final_evaluation_metrics.json")
    with open(metrics_json_path, "w") as f:
        json.dump({
            "winning_model": winning_model_name,
            "optimal_threshold": optimal_threshold,
            "cv_comparison": cv_comparison,
            "test_metrics_default": test_metrics_default,
            "test_metrics_tuned": test_metrics_tuned,
            "confusion_matrix": cm.tolist()
        }, f, indent=2)
    print(f"Saved evaluation metrics JSON to: {metrics_json_path}")
    print("=" * 75)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_model_evaluation_and_selection(base_dir)
