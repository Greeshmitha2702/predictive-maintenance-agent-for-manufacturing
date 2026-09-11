import os
import sys
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

# Ensure ml/src is in sys.path for unpickling DomainFeatureEngineer
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
ML_SRC_DIR = os.path.join(PROJECT_ROOT, "ml", "src")
if ML_SRC_DIR not in sys.path:
    sys.path.insert(0, ML_SRC_DIR)

from schemas.prediction import ExplanationResponse, FeatureContribution
from services.failure_service import get_failure_service

logger = logging.getLogger(__name__)


class ShapExplainabilityService:
    """
    Dedicated service for SHAP feature attribution explainability.
    
    Reuses the exact trained preprocessing pipeline and model from FailurePredictionService,
    extracts feature attributions for failure risk, formats directions, and attaches
    disclaimers clarifying risk contributions vs guaranteed physical root cause.
    """
    _instance: Optional["ShapExplainabilityService"] = None

    def __init__(self):
        self.failure_service = get_failure_service()
        self.explainer = None
        self.shap_available = False
        self._init_explainer()

    def _init_explainer(self) -> None:
        try:
            import shap
            model = self.failure_service.model
            if model is not None:
                self.explainer = shap.TreeExplainer(model)
                self.shap_available = True
        except Exception as exc:
            logger.warning("SHAP TreeExplainer initialization failed: %s", exc, exc_info=True)
            self.explainer = None
            self.shap_available = False

    def explain(self, input_data: Dict[str, Any], top_k: int = 5) -> ExplanationResponse:
        """
        Computes SHAP feature contributions for the provided machine operating parameters.
        Returns ExplanationResponse containing top_k factors, impact directions, and disclaimer.
        """
        public_unavailable_msg = "SHAP explanation unavailable for the current prediction."

        if not self.shap_available or self.explainer is None:
            logger.info("SHAP explainer is not available; returning empty explanation.")
            return ExplanationResponse(
                top_factors=[],
                disclaimer=public_unavailable_msg
            )

        try:
            df_input = pd.DataFrame([input_data])
            
            # Reuse exact failure service preprocessing
            if self.failure_service.engineer is not None:
                df_eng = self.failure_service.engineer.transform(df_input)
            else:
                df_eng = df_input
                
            if self.failure_service.preprocessor is not None:
                X_proc = self.failure_service.preprocessor.transform(df_eng)
            else:
                X_proc = df_eng

            # Recover feature names
            feature_names = self.failure_service.bundle.get("feature_names")
            if not feature_names and hasattr(self.failure_service.preprocessor, "get_feature_names_out"):
                feature_names = list(self.failure_service.preprocessor.get_feature_names_out())
            if not feature_names:
                if isinstance(X_proc, pd.DataFrame):
                    feature_names = list(X_proc.columns)
                else:
                    feature_names = [f"feature_{i}" for i in range(X_proc.shape[1])]

            # Compute local SHAP values
            shap_vals = self.explainer.shap_values(X_proc)
            shap_values_matrix = None

            if isinstance(shap_vals, list) and len(shap_vals) > 1:
                shap_values_matrix = shap_vals[1][0]
            elif isinstance(shap_vals, np.ndarray):
                if shap_vals.ndim == 3:
                    shap_values_matrix = shap_vals[0, :, 1]
                elif shap_vals.ndim == 2:
                    shap_values_matrix = shap_vals[0]
                else:
                    shap_values_matrix = shap_vals.flatten()

            if shap_values_matrix is None:
                logger.error("Failed to extract SHAP value matrix from explainer output.")
                return ExplanationResponse(
                    top_factors=[],
                    disclaimer=public_unavailable_msg
                )

            # Format top factors using signed SHAP contributions
            contributions: List[FeatureContribution] = []
            raw_tuples = []
            for idx, feat_name in enumerate(feature_names):
                val = float(shap_values_matrix[idx])
                raw_tuples.append((feat_name, val))

            # Sort by absolute SHAP contribution magnitude
            raw_tuples.sort(key=lambda x: abs(x[1]), reverse=True)

            for feat_name, val in raw_tuples[:top_k]:
                clean_name = str(feat_name).replace("num__", "").replace("cat__", "")
                direction = "increases_failure_risk" if val > 0 else "decreases_failure_risk"
                contributions.append(
                    FeatureContribution(
                        feature=clean_name,
                        contribution=round(val, 4),
                        direction=direction,
                    )
                )

            standard_disclaimer = (
                "SHAP feature attributions describe statistical model risk contributions/potential "
                "contributing factors, not guaranteed physical root causes."
            )

            return ExplanationResponse(
                top_factors=contributions,
                disclaimer=standard_disclaimer,
            )

        except Exception as exc:
            logger.error("Error generating SHAP explanation: %s", exc, exc_info=True)
            return ExplanationResponse(
                top_factors=[],
                disclaimer=public_unavailable_msg,
            )


def get_shap_service() -> ShapExplainabilityService:
    """Cached singleton getter for ShapExplainabilityService."""
    if ShapExplainabilityService._instance is None:
        ShapExplainabilityService._instance = ShapExplainabilityService()
    return ShapExplainabilityService._instance
