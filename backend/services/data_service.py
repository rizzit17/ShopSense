import json
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUDIT_FILE = BASE_DIR / "data" / "processed" / "preprocessing_audit.json"
PROFILES_FILE = BASE_DIR / "ml" / "artifacts" / "cluster_profiles.json"

class DataService:
    def __init__(self):
        self._audit = None
        self._load_data()

    def _load_data(self):
        if AUDIT_FILE.exists():
            with open(AUDIT_FILE, "r") as f:
                self._audit = json.load(f)
        else:
            self._audit = None

    def get_overview(self) -> Dict[str, Any]:
        if not self._audit:
            self._load_data()
        
        if not self._audit:
            raise FileNotFoundError("Preprocessing audit not found. Run ml/preprocess.py first.")

        if not PROFILES_FILE.exists():
            raise FileNotFoundError("Cluster profiles missing. Run ml/train.py first.")
        profiles = json.loads(PROFILES_FILE.read_text())
        segments_count = len(profiles)

        return {
            "total_customers": self._audit.get("unique_customers", 0),
            "total_revenue_gbp": self._audit.get("total_revenue_gbp", 0.0),
            "total_orders": self._audit.get("total_orders", 0),
            "total_raw_rows": self._audit.get("raw_rows", 0),
            "total_clean_rows": self._audit.get("total_clean_rows", 0),
            "retention_rate_pct": self._audit.get("retention_rate_pct", 0.0),
            "discovered_segments_count": segments_count,
            "time_period_start": self._audit.get("min_date", ""),
            "time_period_end": self._audit.get("max_date", ""),
            "reference_date": self._audit.get("reference_date", ""),
            "cleaning_steps": self._audit.get("steps", [])
        }

data_service = DataService()

