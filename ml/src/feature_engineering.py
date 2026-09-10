import os
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

class DomainFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Custom Scikit-Learn Transformer to construct physical domain features:
    1. Temperature Difference: Process Temperature - Air Temperature (in K)
    2. Mechanical Power (W): Torque [Nm] * Rotational Speed [rpm] * (2 * pi / 60)
    3. Overstrain Index: Tool Wear [min] * Torque [Nm]
    """
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_out = X.copy()
        
        # Map snake_case API contract keys to internal dataset column names if present
        col_mapping = {
            'type': 'Type',
            'air_temperature': 'Air temperature [K]',
            'process_temperature': 'Process temperature [K]',
            'rotational_speed': 'Rotational speed [rpm]',
            'torque': 'Torque [Nm]',
            'tool_wear': 'Tool wear [min]'
        }
        renames = {k: v for k, v in col_mapping.items() if k in X_out.columns}
        if renames:
            X_out = X_out.rename(columns=renames)
            
        # 1. Temperature difference (K)
        X_out['temperature_difference'] = (
            X_out['Process temperature [K]'] - X_out['Air temperature [K]']
        )
        
        # 2. Mechanical Power (Watts) = Torque (Nm) * Angular Velocity (rad/s)
        # rad/s = rpm * (2 * pi / 60)
        X_out['mechanical_power_W'] = (
            X_out['Torque [Nm]'] * X_out['Rotational speed [rpm]'] * (2 * np.pi / 60.0)
        )
        
        # 3. Overstrain Load Index = Tool wear (min) * Torque (Nm)
        X_out['overstrain_index'] = (
            X_out['Tool wear [min]'] * X_out['Torque [Nm]']
        )
        
        return X_out

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        col_mapping = {
            'type': 'Type',
            'air_temperature': 'Air temperature [K]',
            'process_temperature': 'Process temperature [K]',
            'rotational_speed': 'Rotational speed [rpm]',
            'torque': 'Torque [Nm]',
            'tool_wear': 'Tool wear [min]'
        }
        mapped_inputs = [col_mapping.get(f, f) for f in input_features]
        return mapped_inputs + ['temperature_difference', 'mechanical_power_W', 'overstrain_index']


def build_preprocessing_pipeline(categorical_cols, numerical_cols):
    """
    Builds a reusable Scikit-Learn ColumnTransformer that:
    - One-hot encodes categorical variables ('Type').
    - Standardizes numerical features while preserving exact feature names for SHAP.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), categorical_cols),
            ('num', StandardScaler(), numerical_cols)
        ],
        remainder='passthrough',
        verbose_feature_names_out=False
    )
    
    return preprocessor


def process_and_save_data(input_csv_path: str, models_dir: str, data_dir: str):
    """
    Full reproducible pipeline for loading clean data, feature engineering,
    train/test splitting, fitting preprocessor ONLY on train set, and saving artifacts.
    """
    print("=" * 65)
    print(" 1. LOADING CLEANED DATASET")
    print("=" * 65)
    df = pd.read_csv(input_csv_path)
    print(f"Loaded dataset from: {input_csv_path}")
    print(f"Raw shape: {df.shape}")

    # Exclude IDs & Leakage Columns (TWF, HDF, PWF, OSF, RNF)
    target_col = 'Machine failure'
    excluded_cols = ['UDI', 'Product ID', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    
    feature_cols = [c for c in df.columns if c not in excluded_cols and c != target_col]
    
    X = df[feature_cols].copy()
    y = df[target_col].copy()

    print(f"Features ({len(feature_cols)}): {feature_cols}")
    print(f"Target: {target_col}")

    # Step 1: Apply Domain Feature Engineering
    print("\n" + "=" * 65)
    print(" 2. APPLYING DOMAIN FEATURE ENGINEERING")
    print("=" * 65)
    engineer = DomainFeatureEngineer()
    X_engineered = engineer.transform(X)
    
    engineered_feature_list = engineer.get_feature_names_out(feature_cols)
    print("Features after domain engineering:")
    for f in engineered_feature_list:
        print(f"  - {f}")

    # Categorical and Numerical grouping
    categorical_cols = ['Type']
    numerical_cols = [c for c in X_engineered.columns if c not in categorical_cols]

    # Step 2: Train/Test Split (Stratified 80/20 split)
    print("\n" + "=" * 65)
    print(" 3. STRATIFIED TRAIN/TEST SPLIT (80/20)")
    print("=" * 65)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_engineered, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"X_train raw shape: {X_train_raw.shape}")
    print(f"X_test raw shape:  {X_test_raw.shape}")
    print(f"y_train distribution:\n{y_train.value_counts(normalize=True)}")

    # Step 3: Fit ColumnTransformer ONLY on Training Data
    print("\n" + "=" * 65)
    print(" 4. FITTING PREPROCESSOR ON TRAINING SET ONLY")
    print("=" * 65)
    preprocessor = build_preprocessing_pipeline(categorical_cols, numerical_cols)
    
    # Fit & Transform Train, Transform Test
    X_train_proc = preprocessor.fit_transform(X_train_raw)
    X_test_proc = preprocessor.transform(X_test_raw)
    
    # Recover exact feature names for SHAP explainability
    feature_names = preprocessor.get_feature_names_out()
    print("Final Processed Feature Names (SHAP Recoverable):")
    for name in feature_names:
        print(f"  • {name}")

    # Convert back to DataFrame with recovered feature names
    X_train_df = pd.DataFrame(X_train_proc, columns=feature_names)
    X_test_df = pd.DataFrame(X_test_proc, columns=feature_names)

    # Step 4: Save Artifacts & Processed Data
    print("\n" + "=" * 65)
    print(" 5. SAVING PREPROCESSOR & PROCESSED DATASETS")
    print("=" * 65)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)

    preprocessor_path = os.path.join(models_dir, "preprocessor.joblib")
    joblib.dump(preprocessor, preprocessor_path)
    print(f"Saved fitted preprocessor object to: {preprocessor_path}")

    # Save processed CSVs
    X_train_df.to_csv(os.path.join(data_dir, "X_train_processed.csv"), index=False)
    X_test_df.to_csv(os.path.join(data_dir, "X_test_processed.csv"), index=False)
    y_train.to_csv(os.path.join(data_dir, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(data_dir, "y_test.csv"), index=False)
    
    print(f"Saved processed dataset splits to: {data_dir}")
    print("  - X_train_processed.csv")
    print("  - X_test_processed.csv")
    print("  - y_train.csv")
    print("  - y_test.csv")
    print("=" * 65)
    print("Feature Engineering & Preprocessing Complete!")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    clean_data_path = os.path.join(base_dir, "data", "cleaned_predictive_maintenance.csv")
    if not os.path.exists(clean_data_path):
        clean_data_path = os.path.join(base_dir, "data", "ai4i2020.csv")
    
    models_directory = os.path.join(base_dir, "ml", "models")
    data_directory = os.path.join(base_dir, "data")
    
    process_and_save_data(clean_data_path, models_directory, data_directory)
