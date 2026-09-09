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
    roc_auc_score, average_precision_score, precision_score, 
    recall_score, f1_score, classification_report, confusion_matrix
)

# Import local preprocessor builder if needed
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from feature_engineering import DomainFeatureEngineer, build_preprocessing_pipeline

def load_data_and_preprocess(base_dir: str):
    """
    Loads dataset, executes feature engineering, performs 80/20 stratified split,
    and fits ColumnTransformer ONLY on training data.
    """
    data_path = os.path.join(base_dir, "data", "cleaned_predictive_maintenance.csv")
    if not os.path.exists(data_path):
        data_path = os.path.join(base_dir, "data", "ai4i2020.csv")
        
    df = pd.read_csv(data_path)
    
    target_col = 'Machine failure'
    excluded_cols = ['UDI', 'Product ID', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    feature_cols = [c for c in df.columns if c not in excluded_cols and c != target_col]
    
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    
    # 1. Feature Engineering
    engineer = DomainFeatureEngineer()
    X_eng = engineer.transform(X)
    
    categorical_cols = ['Type']
    numerical_cols = [c for c in X_eng.columns if c not in categorical_cols]
    
    # 2. Stratified 80/20 Train/Test Split
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_eng, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 3. Fit Preprocessor ONLY on Training Data
    preprocessor = build_preprocessing_pipeline(categorical_cols, numerical_cols)
    X_train_proc = preprocessor.fit_transform(X_train_raw)
    X_test_proc = preprocessor.transform(X_test_raw)
    
    feature_names = preprocessor.get_feature_names_out()
    
    X_train = pd.DataFrame(X_train_proc, columns=feature_names)
    X_test = pd.DataFrame(X_test_proc, columns=feature_names)
    
    return X_train, X_test, y_train.values, y_test.values, preprocessor, feature_names


def train_and_evaluate_models(X_train, X_test, y_train, y_test, models_dir: str):
    """
    Trains candidate models using 5-Fold Stratified CV on training data only.
    Evaluates final candidate models on test set once and exports best model.
    """
    print("=" * 70)
    print(" ML-3: MODEL TRAINING & COMPARATIVE EVALUATION")
    print("=" * 70)
    
    # Calculate scale_pos_weight for XGBoost
    neg_count = np.sum(y_train == 0)
    pos_count = np.sum(y_train == 1)
    scale_pos_weight = neg_count / pos_count
    
    models = {
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
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ['roc_auc', 'average_precision', 'f1', 'precision', 'recall']
    
    cv_results_summary = []
    trained_models = {}
    
    print("\n--- Phase 1: 5-Fold Stratified Cross-Validation (Training Set Only) ---")
    for name, model in models.items():
        cv_res = cross_validate(model, X_train, y_train, cv=skf, scoring=scoring)
        
        auc_mean = np.mean(cv_res['test_roc_auc'])
        auc_std = np.std(cv_res['test_roc_auc'])
        pr_auc_mean = np.mean(cv_res['test_average_precision'])
        f1_mean = np.mean(cv_res['test_f1'])
        prec_mean = np.mean(cv_res['test_precision'])
        rec_mean = np.mean(cv_res['test_recall'])
        
        cv_results_summary.append({
            "Model": name,
            "CV ROC-AUC": f"{auc_mean:.4f} ± {auc_std:.4f}",
            "CV PR-AUC": f"{pr_auc_mean:.4f}",
            "CV F1-Score": f"{f1_mean:.4f}",
            "CV Precision": f"{prec_mean:.4f}",
            "CV Recall": f"{rec_mean:.4f}"
        })
        
        # Fit model on full training set for test evaluation
        model.fit(X_train, y_train)
        trained_models[name] = model

    cv_df = pd.DataFrame(cv_results_summary)
    print(cv_df.to_string(index=False))

    print("\n--- Phase 2: Final Holdout Test Set Evaluation (Evaluated Once) ---")
    test_results = []
    best_model_name = None
    best_test_auc = -1.0
    
    for name, model in trained_models.items():
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        test_auc = roc_auc_score(y_test, y_prob)
        test_pr_auc = average_precision_score(y_test, y_prob)
        test_f1 = f1_score(y_test, y_pred)
        test_prec = precision_score(y_test, y_pred)
        test_rec = recall_score(y_test, y_pred)
        
        test_results.append({
            "Model": name,
            "Test ROC-AUC": round(test_auc, 4),
            "Test PR-AUC": round(test_pr_auc, 4),
            "Test F1-Score": round(test_f1, 4),
            "Test Precision": round(test_prec, 4),
            "Test Recall": round(test_rec, 4)
        })
        
        if test_auc > best_test_auc:
            best_test_auc = test_auc
            best_model_name = name

    test_df = pd.DataFrame(test_results)
    print(test_df.to_string(index=False))
    
    print(f"\n★ Selected Candidate Model for ML-4 Explainability: {best_model_name} (Test ROC-AUC: {best_test_auc:.4f}) ★\n")
    
    # Save artifacts for ML-4 (XAI)
    os.makedirs(models_dir, exist_ok=True)
    best_model_path = os.path.join(models_dir, "best_model.joblib")
    joblib.dump(trained_models[best_model_name], best_model_path)
    print(f"Best model artifact saved to: {best_model_path}")
    
    results_json_path = os.path.join(models_dir, "model_results.json")
    with open(results_json_path, "w") as f:
        json.dump({
            "best_model": best_model_name,
            "cv_results": cv_results_summary,
            "test_results": test_results
        }, f, indent=2)
    print(f"Results summary saved to: {results_json_path}")
    print("=" * 70)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    models_dir = os.path.join(base_dir, "ml", "models")
    
    X_train, X_test, y_train, y_test, preprocessor, feature_names = load_data_and_preprocess(base_dir)
    train_and_evaluate_models(X_train, X_test, y_train, y_test, models_dir)

if __name__ == "__main__":
    main()
