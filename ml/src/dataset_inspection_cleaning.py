import os
import pandas as pd
import numpy as np

def load_and_inspect_dataset(data_path: str):
    """
    Load AI4I 2020 Predictive Maintenance Dataset and perform initial inspection.
    """
    print("=" * 60)
    print(" 1. LOADING DATASET")
    print("=" * 60)
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset file not found at path: {data_path}")
    
    df = pd.read_csv(data_path)
    print(f"Dataset successfully loaded from: {data_path}")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
    
    print("=" * 60)
    print(" 2. DATASET SUMMARY & DATA TYPES")
    print("=" * 60)
    print(df.info())
    print("\n")
    
    print("=" * 60)
    print(" 3. MISSING VALUES & DUPLICATES CHECK")
    print("=" * 60)
    missing_vals = df.isnull().sum()
    print("Missing values per column:")
    print(missing_vals)
    duplicate_count = df.duplicated().sum()
    print(f"\nTotal duplicate rows: {duplicate_count}\n")
    
    print("=" * 60)
    print(" 4. TARGET CLASS DISTRIBUTION ('Machine failure')")
    print("=" * 60)
    if 'Machine failure' in df.columns:
        class_counts = df['Machine failure'].value_counts()
        class_percents = df['Machine failure'].value_counts(normalize=True) * 100
        dist_df = pd.DataFrame({'Count': class_counts, 'Percentage (%)': class_percents})
        print(dist_df)
    else:
        print("Warning: 'Machine failure' column not found.")
    print("\n")
    
    print("=" * 60)
    print(" 5. SUMMARY STATISTICS FOR NUMERIC FEATURES")
    print("=" * 60)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print(df[numeric_cols].describe().T[['mean', 'std', 'min', '25%', '50%', '75%', 'max']])
    print("\n")
    
    return df

def clean_and_prepare_dataset(df: pd.DataFrame):
    """
    Validates physical boundaries, drops identifiers and target leakage columns,
    and returns feature matrix X and target y.
    """
    print("=" * 60)
    print(" 6. DATA VALIDATION & FEATURE SELECTION")
    print("=" * 60)
    
    # 1. Define excluded features (Identifiers & Target Leakage)
    excluded_cols = ['UDI', 'Product ID', 'TWF', 'HDF', 'PWF', 'OSF', 'RNF']
    target_col = 'Machine failure'
    
    candidate_features = ['Type', 'Air temperature [K]', 'Process temperature [K]', 
                          'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
    
    print(f"Excluded Columns (Identifiers & Failure Modes): {excluded_cols}")
    print(f"Candidate Predictive Features: {candidate_features}")
    print(f"Target Column: {target_col}\n")
    
    # 2. Physical Value Bounds Validation
    print("Checking physical validity bounds:")
    valid_mask = (
        (df['Air temperature [K]'] > 0) &
        (df['Process temperature [K]'] > 0) &
        (df['Rotational speed [rpm]'] >= 0) &
        (df['Torque [Nm]'] >= 0) &
        (df['Tool wear [min]'] >= 0)
    )
    invalid_count = len(df) - valid_mask.sum()
    print(f"Invalid physical value rows count: {invalid_count}")
    
    # 3. Categorical Quality Type Validation
    valid_types = ['L', 'M', 'H']
    type_invalid_count = (~df['Type'].isin(valid_types)).sum()
    print(f"Invalid 'Type' category rows count: {type_invalid_count}")
    
    # 4. Filter dataset (Remove any physically invalid rows if present)
    cleaned_df = df[valid_mask & df['Type'].isin(valid_types)].copy()
    
    # 5. Outlier Policy Notice:
    # Operating extremes (high torque, low speed, high tool wear) are NOT blindly removed
    # because machine failures naturally occur near these operational boundaries.
    print("Outlier Policy: Meaningful operating extremes are preserved for anomaly and failure detection.\n")
    
    # 6. Extract Cleaned Feature Subset + Target
    final_cols = candidate_features + [target_col]
    cleaned_subset = cleaned_df[final_cols].copy()
    
    return cleaned_subset

def main():
    # File paths relative to execution root or project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_path = os.path.join(base_dir, "data", "ai4i2020.csv")
    output_path = os.path.join(base_dir, "data", "cleaned_predictive_maintenance.csv")
    
    # In case script is run directly from workspace root
    if not os.path.exists(input_path):
        input_path = os.path.join("data", "ai4i2020.csv")
        output_path = os.path.join("data", "cleaned_predictive_maintenance.csv")
        
    df_raw = load_and_inspect_dataset(input_path)
    df_cleaned = clean_and_prepare_dataset(df_raw)
    
    # Save cleaned dataset artifact
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_cleaned.to_csv(output_path, index=False)
    print("=" * 60)
    print(" 7. ARTIFACT EXPORT")
    print("=" * 60)
    print(f"Cleaned dataset saved successfully to: {output_path}")
    print(f"Final Cleaned Dataset Shape: {df_cleaned.shape}")

if __name__ == "__main__":
    main()
