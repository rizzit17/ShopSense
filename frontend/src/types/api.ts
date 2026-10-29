export interface CleaningStep {
  step: number;
  name: string;
  excluded: number;
  remaining: number;
  description: string;
}

export interface DatasetOverview {
  total_customers: number;
  total_revenue_gbp: number;
  total_orders: number;
  total_raw_rows: number;
  total_clean_rows: number;
  retention_rate_pct: number;
  discovered_segments_count: number;
  time_period_start: string;
  time_period_end: string;
  reference_date: string;
  cleaning_steps: CleaningStep[];
}

export interface SegmentProfile {
  cluster_id: number;
  name: string;
  badge: string;
  color: string;
  count: number;
  percentage: number;
  display_rank: number;
  description: string;
  characteristics: string[];
  business_insight: string;
  Recency_median: number;
  Recency_mean: number;
  Frequency_median: number;
  Frequency_mean: number;
  Monetary_median: number;
  Monetary_mean: number;
  r_diff: string;
  f_diff: string;
  m_diff: string;
}

export interface CandidateKEval {
  k: number;
  inertia: number;
  silhouette: number;
  davies_bouldin: number;
  calinski_harabasz: number;
  cluster_sizes: number[];
  min_cluster_pct: number;
}

export interface ExperimentDetail {
  name: string;
  description: string;
  results: CandidateKEval[];
  finding: string;
}

export interface EvaluationResponse {
  random_seed: number;
  n_init: number;
  selection_reason: string;
  selected_k: number;
  n_customers: number;
  silhouette_score: number;
  davies_bouldin_index: number;
  calinski_harabasz_score: number;
  inertia: number;
  pca_total_variance_pct: number;
  pca_explained_variance_ratio: number[];
  population_medians: {
    Recency: number;
    Frequency: number;
    Monetary: number;
  };
  population_means: {
    Recency: number;
    Frequency: number;
    Monetary: number;
  };
  candidate_k_evaluation: CandidateKEval[];
  experiment_comparison: {
    experiment_a_raw: ExperimentDetail;
    experiment_b_log: ExperimentDetail;
  };
}

export interface ScatterPoint {
  customer_id: number;
  cluster_id: number;
  segment_name: string;
  color: string;
  pca1: number;
  pca2: number;
  recency: number;
  frequency: number;
  monetary: number;
}

export interface VisualizationResponse {
  total_customers: number;
  pca_explained_variance_ratio: number[];
  total_points: number;
  pca_variance_pct: number;
  points: ScatterPoint[];
  clusters: {
    cluster_id: number;
    name: string;
    badge: string;
    color: string;
    count: number;
    percentage: number;
  }[];
}

export interface PredictRequest {
  recency: number;
  frequency: number;
  monetary: number;
}

export interface PredictResponse {
  cluster_id: number;
  segment_name: string;
  badge: string;
  color: string;
  description: string;
  business_insight: string;
  characteristics: string[];
  input_values: {
    recency: number;
    frequency: number;
    monetary: number;
  };
  cluster_medians: {
    recency: number;
    frequency: number;
    monetary: number;
  };
  comparison: {
    recency_comparison: string;
    frequency_comparison: string;
    monetary_comparison: string;
  };
  is_outlier: boolean;
  outlier_warning?: string | null;
}

