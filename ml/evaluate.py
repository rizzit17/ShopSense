"""
ShopSense - Model & Cluster Evaluation CLI
Prints academic evaluation metrics, cluster profiles, and experiment comparisons.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "ml" / "artifacts"
AUDIT_FILE = BASE_DIR / "data" / "processed" / "preprocessing_audit.json"

def display_evaluation():
    print("=" * 70)
    print("SHOPSENSE — UNSUPERVISED ML EVALUATION & CLUSTERING REPORT")
    print("=" * 70)

    if AUDIT_FILE.exists():
        with open(AUDIT_FILE) as f:
            audit = json.load(f)
        print("\n1. DATA PREPROCESSING AUDIT TRAIL:")
        print(f"   Raw Transactions Loaded:      {audit['raw_rows']:,}")
        for s in audit["steps"]:
            print(f"   - Step {s['step']} ({s['name']}): Excluded {s['excluded']:,} -> {s['remaining']:,} rows")
        print(f"   Final Valid Transactions:     {audit['total_clean_rows']:,} ({audit['retention_rate_pct']}% retention)")
        print(f"   Positive Recorded Spending:          £{audit['total_revenue_gbp']:,.2f}")
        print(f"   Unique Valid Customers:       {audit['unique_customers']:,}")

    metrics_file = ARTIFACTS_DIR / "evaluation_metrics.json"
    profiles_file = ARTIFACTS_DIR / "cluster_profiles.json"
    comparison_file = ARTIFACTS_DIR / "experiment_comparison.json"

    if not metrics_file.exists() or not profiles_file.exists():
        print("[ERROR] ML artifacts not found. Please run ml/train.py first.")
        return

    with open(metrics_file) as f:
        metrics = json.load(f)
    with open(profiles_file) as f:
        profiles = json.load(f)
    with open(comparison_file) as f:
        comp = json.load(f)

    print("\n2. PRIMARY MODEL CLUSTERING METRICS:")
    print(f"   Selected K:                   {metrics['selected_k']}")
    print(f"   Silhouette Score:             {metrics['silhouette_score']}")
    print(f"   Davies-Bouldin Index:         {metrics['davies_bouldin_index']} (lower is better)")
    print(f"   Calinski-Harabasz Score:      {metrics['calinski_harabasz_score']} (higher is better)")
    print(f"   Within-Cluster Inertia:       {metrics['inertia']}")
    print(f"   PCA 2D Variance Captured:     {metrics['pca_total_variance_pct']}%")

    print("\n3. CANDIDATE K EVALUATION (K=2..8):")
    print(f"   {'K':<4} | {'Inertia':<10} | {'Silhouette':<12} | {'Davies-Bouldin':<15} | {'Calinski-Harabasz':<18} | {'Min Cluster %'}")
    print("   " + "-" * 75)
    for c in metrics["candidate_k_evaluation"]:
        print(f"   {c['k']:<4} | {c['inertia']:<10.1f} | {c['silhouette']:<12.4f} | {c['davies_bouldin']:<15.4f} | {c['calinski_harabasz']:<18.1f} | {c['min_cluster_pct']:.1f}%")

    print("\n4. DISCOVERED SHOPPING PERSONALITIES (K=4):")
    for p in profiles:
        print(f"\n   [Cluster {p['cluster_id']}: {p['name']}] - {p['badge']}")
        print(f"   - Size:        {p['count']:,} customers ({p['percentage']}%)")
        print(f"   - Recency:     Median {p['Recency_median']:.0f} days (Mean: {p['Recency_mean']:.1f} days)")
        print(f"   - Frequency:   Median {p['Frequency_median']:.0f} orders (Mean: {p['Frequency_mean']:.1f} orders)")
        print(f"   - Monetary:    Median £{p['Monetary_median']:,.2f} (Mean: £{p['Monetary_mean']:,.2f})")
        print(f"   - Profile:     {p['description']}")
        print(f"   - Insight:     {p['business_insight']}")

    print("\n5. EXPERIMENTAL COMPARISON (RAW VS LOG1P):")
    print(f"   {comp['experiment_a_raw']['name']}:")
    print(f"   -> {comp['experiment_a_raw']['finding']}")
    print(f"   {comp['experiment_b_log']['name']}:")
    print(f"   -> {comp['experiment_b_log']['finding']}")
    print("=" * 70)

if __name__ == "__main__":
    display_evaluation()

