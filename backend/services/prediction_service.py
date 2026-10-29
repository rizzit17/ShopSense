import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple
from backend.services.clustering_service import clustering_service

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_DIR = BASE_DIR / "ml" / "artifacts"

class PredictionService:
    def __init__(self):
        self._model = None
        self._scaler = None
        self._pipeline = None
        self._ranges = None
        self._pca = None
        self._load_artifacts()

    def _load_artifacts(self):
        model_path = ARTIFACTS_DIR / "kmeans_model.joblib"
        scaler_path = ARTIFACTS_DIR / "scaler.joblib"
        pca_path = ARTIFACTS_DIR / "pca_model.joblib"

        pipeline_path = ARTIFACTS_DIR / "prediction_pipeline.joblib"
        metrics_path = ARTIFACTS_DIR / "evaluation_metrics.json"
        if pipeline_path.exists() and metrics_path.exists():
            import json
            self._pipeline = joblib.load(pipeline_path)
            self._ranges = json.loads(metrics_path.read_text())["training_ranges"]
        if model_path.exists() and scaler_path.exists():
            self._model = joblib.load(model_path)
            self._scaler = joblib.load(scaler_path)
            if pca_path.exists():
                self._pca = joblib.load(pca_path)

    def predict(self, recency: float, frequency: int, monetary: float) -> Dict[str, Any]:
        if self._pipeline is None or self._ranges is None:
            self._load_artifacts()
        if self._pipeline is None or self._ranges is None:
            raise FileNotFoundError("ML model or scaler artifact not found. Please run ml/train.py first.")

        # Outlier bounds derived from historical training data
        is_outlier = False
        outlier_reasons = []

        for name, value in zip(("Recency", "Frequency", "Monetary"), (recency, frequency, monetary)):
            bounds = self._ranges[name]
            if value < bounds["min"] or value > bounds["max"]:
                is_outlier = True
                outlier_reasons.append(f"{name} of {value:,.2f} exceeds the observed training range [{bounds['min']:,.2f}, {bounds['max']:,.2f}].")
        outlier_warning = " | ".join(outlier_reasons) if outlier_reasons else None
        x_raw = np.array([[recency, frequency, monetary]], dtype=float)
        if not np.isfinite(x_raw).all() or recency < 0 or frequency < 1 or monetary <= 0:
            raise ValueError("RFM inputs must be finite; recency >= 0, frequency >= 1, monetary > 0")
        cluster_id = int(self._pipeline.predict(x_raw)[0])

        # Lookup cluster profile
        profile = clustering_service.get_segment_by_id(cluster_id)
        if not profile:
            raise ValueError(f"Profile for predicted cluster {cluster_id} not found.")

        # Relative comparisons to cluster medians
        r_med = profile["Recency_median"]
        f_med = profile["Frequency_median"]
        m_med = profile["Monetary_median"]

        r_comp = "More recent than typical" if recency < r_med else ("Similar to segment median" if recency == r_med else "Less recent than typical")
        f_comp = "Higher order count than median" if frequency > f_med else ("Matches segment median" if frequency == f_med else "Lower order count than median")
        m_ratio = monetary / m_med if m_med > 0 else 1.0
        m_comp = f"{m_ratio:.1f}x of segment median spend (£{m_med:,.2f})"

        return {
            "cluster_id": cluster_id,
            "segment_name": profile["name"],
            "badge": profile["badge"],
            "color": profile["color"],
            "description": profile["description"],
            "business_insight": profile["business_insight"],
            "characteristics": profile["characteristics"],
            "input_values": {
                "recency": float(recency),
                "frequency": float(frequency),
                "monetary": round(float(monetary), 2)
            },
            "cluster_medians": {
                "recency": r_med,
                "frequency": f_med,
                "monetary": m_med
            },
            "comparison": {
                "recency_comparison": r_comp,
                "frequency_comparison": f_comp,
                "monetary_comparison": m_comp
            },
            "is_outlier": is_outlier,
            "outlier_warning": outlier_warning
        }

prediction_service = PredictionService()

