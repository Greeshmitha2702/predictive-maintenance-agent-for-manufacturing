import os
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

# 1. Feature Name Constants
EXCLUDED_COLS = ['UDI', 'Product ID', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
TARGET_COL = 'Machine failure'
BASE_FEATURE_COLS = [
    'Type', 
    'Air temperature [K]', 
    'Process temperature [K]', 
    'Rotational speed [rpm]', 
    'Torque [Nm]', 
    'Tool wear [min]'
]
CATEGORICAL_COLS = ['Type']
NUMERICAL_BASE_COLS = [
    'Air temperature [K]', 
    'Process temperature [K]', 
    'Rotational speed [rpm]', 
    'Torque [Nm]', 
    'Tool wear [min]'
]
ENGINEERED_COLS = [
    'temperature_difference', 
    'mechanical_power_W', 
    'overstrain_index'
]
ALL_NUMERICAL_COLS = NUMERICAL_BASE_COLS + ENGINEERED_COLS

SNAKE_CASE_MAPPING = {
    'type': 'Type',
    'air_temperature': 'Air temperature [K]',
    'process_temperature': 'Process temperature [K]',
    'rotational_speed': 'Rotational speed [rpm]',
    'torque': 'Torque [Nm]',
    'tool_wear': 'Tool wear [min]'
}


class DomainFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Custom Scikit-Learn Transformer to construct physical domain features:
    1. temperature_difference = Process temperature [K] - Air temperature [K]
    2. mechanical_power_W = Torque [Nm] * Rotational speed [rpm] * (2 * pi / 60)
    3. overstrain_index = Tool wear [min] * Torque [Nm]
    
    Supports both raw dataset column names and backend API snake_case keys.
    """
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_out = X.copy()
        if isinstance(X_out, np.ndarray):
            X_out = pd.DataFrame(X_out, columns=BASE_FEATURE_COLS)
            
        # Map snake_case API contract keys to internal dataset column names if present
        renames = {k: v for k, v in SNAKE_CASE_MAPPING.items() if k in X_out.columns}
        if renames:
            X_out = X_out.rename(columns=renames)
            
        # 1. Temperature difference (K)
        X_out['temperature_difference'] = (
            X_out['Process temperature [K]'] - X_out['Air temperature [K]']
        )
        
        # 2. Mechanical Power (Watts) = Torque (Nm) * Angular Velocity (rad/s)
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
            return BASE_FEATURE_COLS + ENGINEERED_COLS
        mapped_inputs = [SNAKE_CASE_MAPPING.get(f, f) for f in input_features]
        return mapped_inputs + ENGINEERED_COLS


def build_preprocessing_pipeline(categorical_cols=None, numerical_cols=None):
    """
    Builds a reusable Scikit-Learn ColumnTransformer that:
    - One-hot encodes categorical variables ('Type').
    - Standardizes numerical features while preserving exact feature names for SHAP.
    """
    if categorical_cols is None:
        categorical_cols = CATEGORICAL_COLS
    if numerical_cols is None:
        numerical_cols = ALL_NUMERICAL_COLS
        
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(sparse_output=False, handle_unknown='ignore'), categorical_cols),
            ('num', StandardScaler(), numerical_cols)
        ],
        remainder='passthrough',
        verbose_feature_names_out=False
    )
    return preprocessor


def build_full_feature_pipeline(categorical_cols=None, numerical_cols=None):
    """
    Returns an un-fitted Scikit-Learn Pipeline combining domain feature engineering 
    and ColumnTransformer preprocessing, ready for ML-3 cross-validation and imblearn pipeline.
    """
    return Pipeline([
        ('engineer', DomainFeatureEngineer()),
        ('preprocessor', build_preprocessing_pipeline(categorical_cols, numerical_cols))
    ])


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    clean_data_path = os.path.join(base_dir, "data", "cleaned_predictive_maintenance.csv")
    if not os.path.exists(clean_data_path):
        clean_data_path = os.path.join(base_dir, "data", "ai4i2020.csv")
    
    print("Testing ML-2 Feature Engineering & Preprocessing Utilities...")
    df = pd.read_csv(clean_data_path)
    X = df[BASE_FEATURE_COLS].copy()
    
    pipeline = build_full_feature_pipeline()
    X_processed = pipeline.fit_transform(X)
    
    feature_names = pipeline.named_steps['preprocessor'].get_feature_names_out()
    print(f"Original Input Shape: {X.shape}")
    print(f"Processed Output Shape: {X_processed.shape}")
    print("Recoverable Feature Names for SHAP:")
    for name in feature_names:
        print(f"  • {name}")
