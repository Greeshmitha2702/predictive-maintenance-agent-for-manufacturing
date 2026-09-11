import os
import sys
import joblib
import pandas as pd
from typing import Tuple, Dict, Any, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
ML_SRC_DIR = os.path.join(PROJECT_ROOT, "ml", "src")
if ML_SRC_DIR not in sys.path:
    sys.path.insert(0, ML_SRC_DIR)


class AnomalyDetectionService:
    """
    Service responsible for loading the trained Isolation Forest anomaly detection pipeline
    and predicting anomaly scores and boolean flags.
    """
    _instance: Optional["AnomalyDetectionService"] = None

    def __init__(self, artifact_path: Optional[str] = None):
        if artifact_path is None:
            artifact_path = os.path.join(PROJECT_ROOT, "ml", "models", "anomaly_pipeline.pkl")
            if not os.path.exists(artifact_path):
                joblib_fallback = os.path.join(PROJECT_ROOT, "ml", "models", "anomaly_pipeline.joblib")
                if os.path.exists(joblib_fallback):
                    artifact_path = joblib_fallback

        self.artifact_path = artifact_path
        self.bundle: Dict[str, Any] = {}
        self.engineer = None
        self.preprocessor = None
        self.model = None
        self.threshold: float = 0.0
        self._load_artifact()

    def _load_artifact(self) -> None:
        if not os.path.exists(self.artifact_path):
            raise RuntimeError(
                f"Anomaly detection model artifact missing at {self.artifact_path}. "
                "Ensure ML anomaly detection training pipeline has exported artifacts."
            )
        try:
            self.bundle = joblib.load(self.artifact_path)
            
            if isinstance(self.bundle, dict):
                self.engineer = self.bundle.get("engineer")
                self.preprocessor = self.bundle.get("preprocessor")
                self.model = self.bundle.get("model")
                self.threshold = float(self.bundle.get("threshold", 0.0))
            else:
                self.model = self.bundle
                self.threshold = 0.0

        except Exception as exc:
            raise RuntimeError(
                f"Failed to load or parse anomaly detection artifact at {self.artifact_path}: {str(exc)}"
            ) from exc

    def detect_anomaly(self, input_data: Dict[str, Any]) -> Tuple[float, bool]:
        """
        Runs anomaly detection on validated input dictionary.
        Returns: (anomaly_score, is_anomaly)
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
            
        # 3. Anomaly Model Inference
        if self.model is None:
            raise RuntimeError("Anomaly detection model is not loaded.")
            
        # decision_function: lower/negative values indicate anomaly
        scores = self.model.decision_function(X_proc)
        raw_score = float(scores[0])
        
        # IsolationForest.predict returns -1 for anomaly, 1 for inlier
        preds = self.model.predict(X_proc)
        is_anomaly = bool(preds[0] == -1)
        
        return round(raw_score, 4), is_anomaly


def get_anomaly_service() -> AnomalyDetectionService:
    """Cached singleton getter for AnomalyDetectionService."""
    if AnomalyDetectionService._instance is None:
        AnomalyDetectionService._instance = AnomalyDetectionService()
    return AnomalyDetectionService._instance
