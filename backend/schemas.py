from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CleaningStep(BaseModel):
    step: int
    name: str
    excluded: int
    remaining: int
    description: str

class DatasetOverview(BaseModel):
    total_customers: int
    total_revenue_gbp: float
    total_orders: int
    total_raw_rows: int
    total_clean_rows: int
    retention_rate_pct: float
    discovered_segments_count: int
    time_period_start: str
    time_period_end: str
    reference_date: str
    cleaning_steps: List[CleaningStep]

class SegmentProfile(BaseModel):
    cluster_id: int
    name: str
    badge: str
    color: str
    count: int
    percentage: float
    display_rank: int
    description: str
    characteristics: List[str]
    business_insight: str
    Recency_median: float
    Recency_mean: float
    Frequency_median: float
    Frequency_mean: float
    Monetary_median: float
    Monetary_mean: float
    r_diff: str
    f_diff: str
    m_diff: str

class CandidateKEval(BaseModel):
    k: int
    inertia: float
    silhouette: float
    davies_bouldin: float
    calinski_harabasz: float
    cluster_sizes: List[int]
    min_cluster_pct: float

class ExperimentDetail(BaseModel):
    name: str
    description: str
    results: List[CandidateKEval]
    finding: str

class ExperimentComparison(BaseModel):
    experiment_a_raw: ExperimentDetail
    experiment_b_log: ExperimentDetail

class TrainingRange(BaseModel):
    min: float
    max: float

class HealthResponse(BaseModel):
    status: str
    service: str
    dataset: str

class ClusterSummary(BaseModel):
    cluster_id: int
    name: str
    badge: str
    color: str
    count: int
    percentage: float

class EvaluationResponse(BaseModel):
    random_seed: int
    n_init: int
    silhouette_sample_size: int
    sklearn_version: str
    selection_reason: str
    training_ranges: Dict[str, TrainingRange]
    selected_k: int
    n_customers: int
    silhouette_score: float
    davies_bouldin_index: float
    calinski_harabasz_score: float
    inertia: float
    pca_total_variance_pct: float
    pca_explained_variance_ratio: List[float]
    population_medians: Dict[str, float]
    population_means: Dict[str, float]
    candidate_k_evaluation: List[CandidateKEval]
    experiment_comparison: ExperimentComparison

class ScatterPoint(BaseModel):
    customer_id: int
    cluster_id: int
    segment_name: str
    color: str
    pca1: float
    pca2: float
    recency: float
    frequency: float
    monetary: float

class VisualizationResponse(BaseModel):
    total_customers: int
    pca_explained_variance_ratio: List[float]
    total_points: int
    pca_variance_pct: float
    points: List[ScatterPoint]
    clusters: List[ClusterSummary]

class PredictRequest(BaseModel):
    model_config = {"allow_inf_nan": False, "extra": "forbid", "strict": True}
    recency: float = Field(..., ge=0, description="Days since last transaction (>= 0)")
    frequency: int = Field(..., ge=1, le=9007199254740991, description="Completed orders, represented as a safe integer")
    monetary: float = Field(..., ge=0.01, description="Total monetary spend in GBP (> 0)")

class PredictResponse(BaseModel):
    cluster_id: int
    segment_name: str
    badge: str
    color: str
    description: str
    business_insight: str
    characteristics: List[str]
    input_values: Dict[str, float]
    cluster_medians: Dict[str, float]
    comparison: Dict[str, str]
    is_outlier: bool
    outlier_warning: Optional[str] = None

