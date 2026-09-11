import os
import sys
import joblib
import pandas as pd
from typing import Tuple, Dict, Any, Optional

# Ensure ml/src is in sys.path for unpickling DomainFeatureEngineer
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
ML_SRC_DIR = os.path.join(PROJECT_ROOT, "ml", "src")
if ML_SRC_DIR not in sys.path:
    sys.path.insert(0, ML_SRC_DIR)


class FailurePredictionService:
    """
    Service responsible for loading the trained failure prediction pipeline
    and predicting machine failure probability and thresholded classification.
    """
    _instance: Optional["FailurePredictionService"] = None

    def __init__(self, artifact_path: Optional[str] = None):
        if artifact_path is None:
            artifact_path = os.path.join(PROJECT_ROOT, "ml", "models", "failure_pipeline.pkl")
            if not os.path.exists(artifact_path):
                joblib_fallback = os.path.join(PROJECT_ROOT, "ml", "models", "final_failure_pipeline.joblib")
                if os.path.exists(joblib_fallback):
                    artifact_path = joblib_fallback

        self.artifact_path = artifact_path
        self.bundle: Dict[str, Any] = {}
        self.engineer = None
        self.preprocessor = None
        self.model = None
        self.threshold: float = 0.50
        self.model_name: str = "FailurePredictionModel"
        self._load_artifact()

    def _load_artifact(self) -> None:
        if not os.path.exists(self.artifact_path):
            raise RuntimeError(
                f"Failure prediction model artifact missing at {self.artifact_path}. "
                "Ensure ML model training and packaging pipelines have been run."
            )
        try:
            self.bundle = joblib.load(self.artifact_path)
            
            if isinstance(self.bundle, dict):
                self.engineer = self.bundle.get("engineer")
                self.preprocessor = self.bundle.get("preprocessor")
                self.model = self.bundle.get("model") or self.bundle.get("classifier")
                
                if "pipeline" in self.bundle:
                    pipe = self.bundle["pipeline"]
                    if hasattr(pipe, "named_steps"):
                        if self.engineer is None:
                            self.engineer = pipe.named_steps.get("engineer")
                        if self.preprocessor is None:
                            self.preprocessor = pipe.named_steps.get("preprocessor")
                        if self.model is None:
                            self.model = pipe.named_steps.get("classifier", pipe.named_steps.get("model"))
                        
                self.threshold = float(
                    self.bundle.get("optimal_threshold") 
                    or self.bundle.get("selected_threshold") 
                    or 0.50
                )
                self.model_name = str(
                    self.bundle.get("model_name") 
                    or self.bundle.get("winning_model_name") 
                    or "RandomForest"
                )
            else:
                pipe = self.bundle
                if hasattr(pipe, "named_steps"):
                    self.engineer = pipe.named_steps.get("engineer")
                    self.preprocessor = pipe.named_steps.get("preprocessor")
                    self.model = pipe.named_steps.get("classifier", pipe.named_steps.get("model"))
                else:
                    self.model = pipe
                self.threshold = 0.50
                self.model_name = type(self.model).__name__

        except Exception as exc:
            raise RuntimeError(
                f"Failed to load or parse failure prediction artifact at {self.artifact_path}: {str(exc)}"
            ) from exc

    def predict(self, input_data: Dict[str, Any]) -> Tuple[float, bool, str]:
        """
        Runs failure prediction on validated input dictionary.
        Returns: (failure_probability, failure_predicted, model_version_string)
        """
        df_input = pd.DataFrame([input_data])
        
        # 1. Feature Engineering
        if self.engineer is not None:
            df_eng = self.engineer.transform(df_input)
        else:
            df_eng = df_input
            
        # 2. Preprocessing
        if self.preprocessor is not None:
            X_proc = self.preprocessor.transform(df_eng)
        else:
            X_proc = df_eng
            
        # 3. Model Inference
        if self.model is None:
            raise RuntimeError("Failure prediction model is not loaded.")
            
        probs = self.model.predict_proba(X_proc)[:, 1]
        failure_prob = float(probs[0])
        failure_pred = bool(failure_prob >= self.threshold)
        version_str = f"{self.model_name} (Threshold: {self.threshold:.4f})"
        
        return round(failure_prob, 4), failure_pred, version_str


def get_failure_service() -> FailurePredictionService:
    """Cached singleton getter for FailurePredictionService."""
    if FailurePredictionService._instance is None:
        FailurePredictionService._instance = FailurePredictionService()
    return FailurePredictionService._instance
