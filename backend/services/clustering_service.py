import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_DIR = BASE_DIR / "ml" / "artifacts"

class ClusteringService:
    def __init__(self):
        self._profiles: Optional[List[Dict[str, Any]]] = None
        self._metrics: Optional[Dict[str, Any]] = None
        self._comparison: Optional[Dict[str, Any]] = None
        self._segments_df: Optional[pd.DataFrame] = None
        self._load()

    def _load(self):
        profiles_path = ARTIFACTS_DIR / "cluster_profiles.json"
        metrics_path = ARTIFACTS_DIR / "evaluation_metrics.json"
        comp_path = ARTIFACTS_DIR / "experiment_comparison.json"
        csv_path = ARTIFACTS_DIR / "customer_segments.csv"

        if profiles_path.exists():
            with open(profiles_path, "r") as f:
                self._profiles = json.load(f)
        if metrics_path.exists():
            with open(metrics_path, "r") as f:
                self._metrics = json.load(f)
        if comp_path.exists():
            with open(comp_path, "r") as f:
                self._comparison = json.load(f)
        if csv_path.exists():
            self._segments_df = pd.read_csv(csv_path)

    def get_segments(self) -> List[Dict[str, Any]]:
        if not self._profiles:
            self._load()
        if not self._profiles:
            raise FileNotFoundError("Cluster profiles artifact not found. Run ml/train.py first.")
        return self._profiles

    def get_segment_by_id(self, cluster_id: int) -> Optional[Dict[str, Any]]:
        segments = self.get_segments()
        for s in segments:
            if s["cluster_id"] == cluster_id:
                return s
        return None

    def get_evaluation(self) -> Dict[str, Any]:
        if not self._metrics or not self._comparison:
            self._load()
        if not self._metrics:
            raise FileNotFoundError("Evaluation metrics artifact not found. Run ml/train.py first.")
        
        data = dict(self._metrics)
        data["experiment_comparison"] = self._comparison or {}
        return data

    def get_visualization(self, sample_limit: int = 5000) -> Dict[str, Any]:
        if self._segments_df is None or not self._profiles:
            self._load()
        if self._segments_df is None or not self._profiles:
            raise FileNotFoundError("Customer segments artifact not found. Run ml/train.py first.")

        df = self._segments_df
        profile_map = {p["cluster_id"]: p for p in self._profiles}

        # Subsample if dataset is large, preserving balanced random distribution
        if len(df) > sample_limit:
            sampled_df = df.sample(n=sample_limit, random_state=42).reset_index(drop=True)
        else:
            sampled_df = df

        points = []
        for _, row in sampled_df.iterrows():
            cid = int(row["Cluster"])
            prof = profile_map.get(cid, {})
            points.append({
                "customer_id": int(row["CustomerID"]),
                "cluster_id": cid,
                "segment_name": prof.get("name", f"Cluster {cid}"),
                "color": prof.get("color", "#718776"),
                "pca1": float(row["PCA1"]),
                "pca2": float(row["PCA2"]),
                "recency": float(row["Recency"]),
                "frequency": float(row["Frequency"]),
                "monetary": float(row["Monetary"])
            })

        cluster_summary = [
            {
                "cluster_id": p["cluster_id"],
                "name": p["name"],
                "badge": p["badge"],
                "color": p["color"],
                "count": p["count"],
                "percentage": p["percentage"]
            }
            for p in self._profiles
        ]

        if not self._metrics:
            raise FileNotFoundError("Evaluation metrics missing. Run ml/train.py first.")
        variance_pct = self._metrics["pca_total_variance_pct"]

        return {
            "total_points": len(points),
            "total_customers": len(df),
            "pca_explained_variance_ratio": self._metrics["pca_explained_variance_ratio"],
            "pca_variance_pct": variance_pct,
            "points": points,
            "clusters": cluster_summary
        }

clustering_service = ClusteringService()
