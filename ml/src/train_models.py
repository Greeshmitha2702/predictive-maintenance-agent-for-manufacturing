import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, average_precision_score, precision_score, 
    recall_score, f1_score
)

# Imbalanced-learn imports for leakage-free SMOTE inside CV folds
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from feature_engineering import (
    DomainFeatureEngineer, 
    build_preprocessing_pipeline,
    EXCLUDED_COLS,
    TARGET_COL,
    BASE_FEATURE_COLS
)


def run_ml3_model_training(base_dir: str):
    """
    ML-3 Model Training Pipeline:
    1. Loads full cleaned dataset (~10,000 rows).
    2. Performs 80/20 Stratified Train/Test split (test set kept untouched for ML-4).
    3. Evaluates 2 approaches via 5-Fold Stratified K-Fold CV on training set:
       - Approach A: Balanced Random Forest (class_weight='balanced')
       - Approach B: SMOTE + Random Forest (SMOTE inside imblearn pipeline)
    4. Compares CV metrics (Recall, Precision, F1, PR-AUC, ROC-AUC).
    5. Selects winning model and fits on full training set.
    6. Saves best model pipeline to ml/models/best_model.joblib and comparison JSON.
    """
    print("=" * 75)
    print(" ML-3: RANDOM FOREST MODEL TRAINING & SMOTE EXPERIMENTATION")
    print("=" * 75)
    
    # 1. Ingest Full Cleaned Dataset (~10,000 rows)
    data_path = os.path.join(base_dir, "data", "cleaned_predictive_maintenance.csv")
    if not os.path.exists(data_path):
        data_path = os.path.join(base_dir, "data", "ai4i2020.csv")
        
    df = pd.read_csv(data_path)
    print(f"Loaded full dataset from: {data_path}")
    print(f"Dataset shape: {df.shape}")
    
    feature_cols = [c for c in df.columns if c not in EXCLUDED_COLS and c != TARGET_COL]
    
    X = df[feature_cols].copy()
    y = df[TARGET_COL].copy()
    
    print(f"Input features ({len(feature_cols)}): {feature_cols}")
    print(f"Target distribution:\n{y.value_counts()}")
    
    # 2. Stratified 80/20 Train/Test Split (Test set remains untouched for ML-4)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTrain set shape: {X_train.shape} (Failures: {y_train.sum()})")
    print(f"Test set shape:  {X_test.shape} (Untouched for ML-4)")
    
    # 3. Define Candidate Pipelines
    # Approach A: Balanced Random Forest Baseline
    pipeline_a = ImbPipeline([
        ('engineer', DomainFeatureEngineer()),
        ('preprocessor', build_preprocessing_pipeline()),
        ('classifier', RandomForestClassifier(
            n_estimators=100, class_weight='balanced', random_state=42, n_jobs=-1
        ))
    ])
    
    # Approach B: SMOTE + Random Forest (SMOTE inside imblearn pipeline to prevent leakage)
    pipeline_b = ImbPipeline([
        ('engineer', DomainFeatureEngineer()),
        ('preprocessor', build_preprocessing_pipeline()),
        ('smote', SMOTE(random_state=42)),
        ('classifier', RandomForestClassifier(
            n_estimators=100, random_state=42, n_jobs=-1
        ))
    ])
    
    candidate_pipelines = {
        "Balanced Random Forest": pipeline_a,
        "SMOTE + Random Forest": pipeline_b
    }
    
    # 4. 5-Fold Stratified Cross-Validation on Training Set
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = {
        'recall': 'recall',
        'precision': 'precision',
        'f1': 'f1',
        'pr_auc': 'average_precision',
        'roc_auc': 'roc_auc'
    }
    
    cv_comparison = []
    
    print("\n--- 5-Fold Stratified Cross-Validation (Training Set Only) ---")
    for name, pipeline in candidate_pipelines.items():
        cv_res = cross_validate(pipeline, X_train, y_train, cv=skf, scoring=scoring, n_jobs=-1)
        
        rec_mean = np.mean(cv_res['test_recall'])
        prec_mean = np.mean(cv_res['test_precision'])
        f1_mean = np.mean(cv_res['test_f1'])
        pr_auc_mean = np.mean(cv_res['test_pr_auc'])
        roc_auc_mean = np.mean(cv_res['test_roc_auc'])
        
        cv_comparison.append({
            "Model": name,
            "CV Recall": round(rec_mean, 4),
            "CV Precision": round(prec_mean, 4),
            "CV F1": round(f1_mean, 4),
            "CV PR-AUC": round(pr_auc_mean, 4),
            "CV ROC-AUC": round(roc_auc_mean, 4)
        })
        
    comp_df = pd.DataFrame(cv_comparison)
    print("\nModel Cross-Validation Comparison Table:")
    print(comp_df.to_string(index=False))
    
    # 5. Model Selection based on CV Metrics (Emphasis on PR-AUC, F1, Recall)
    # Sort by PR-AUC and F1-Score
    sorted_df = comp_df.sort_values(by=['CV PR-AUC', 'CV F1', 'CV Recall'], ascending=False)
    winning_model_name = sorted_df.iloc[0]['Model']
    winning_pipeline = candidate_pipelines[winning_model_name]
    
    print(f"\n★ Winner Selected via CV Evidence: '{winning_model_name}' ★")
    print("  Rationale: Selected for highest PR-AUC and F1-Score on minority failure class during 5-fold CV.\n")
    
    # 6. Fit Winning Pipeline on Entire Training Set & Save Artifacts
    print(f"Fitting winning pipeline ('{winning_model_name}') on complete 80% training set...")
    winning_pipeline.fit(X_train, y_train)
    
    models_dir = os.path.join(base_dir, "ml", "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Extract feature names for SHAP
    preprocessor = winning_pipeline.named_steps['preprocessor']
    feature_names = list(preprocessor.get_feature_names_out())
    
    model_artifact = {
        "pipeline": winning_pipeline,
        "model_name": winning_model_name,
        "feature_names": feature_names,
        "input_feature_cols": feature_cols,
        "cv_metrics": sorted_df.iloc[0].to_dict()
    }
    
    best_model_path = os.path.join(models_dir, "best_model.joblib")
    joblib.dump(model_artifact, best_model_path)
    print(f"Saved winning model artifact to: {best_model_path}")
    
    # Save CV comparison JSON
    cv_json_path = os.path.join(models_dir, "cv_model_comparison.json")
    with open(cv_json_path, "w") as f:
        json.dump({
            "winning_model": winning_model_name,
            "cv_comparison": cv_comparison
        }, f, indent=2)
    print(f"Saved CV comparison results to: {cv_json_path}")
    print("=" * 75)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_ml3_model_training(base_dir)
