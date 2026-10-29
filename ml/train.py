"""
ShopSense - Model Training, Evaluation, and Segmentation Profiling
Trains K-Means on RFM features, compares Experiment A (raw) vs Experiment B (log1p),
evaluates K=2 to 8, computes PCA, generates figures, and saves artifacts.
"""

import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from threadpoolctl import threadpool_limits
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "rfm_raw.csv"
ARTIFACTS_DIR = BASE_DIR / "ml" / "artifacts"
FIGURES_DIR = BASE_DIR / "reports" / "figures"

def generate_personality_profile(cluster_id, stats, pop_medians):
    """
    Derives an interpretable Shopping Personality name and profile based on 
    actual observed median RFM values relative to the overall population.
    """
    r_med = stats["Recency_median"]
    f_med = stats["Frequency_median"]
    m_med = stats["Monetary_median"]

    r_pop = pop_medians["Recency"]
    f_pop = pop_medians["Frequency"]
    m_pop = pop_medians["Monetary"]

    r_diff = "Recent" if r_med <= r_pop else "Dormant"
    f_diff = "High Frequency" if f_med >= f_pop else "Low Frequency"
    m_diff = "High Spend" if m_med >= m_pop else "Modest Spend"

    # Business-interpretable archetypes based on verified behavior
    if r_med <= r_pop and f_med >= f_pop and m_med >= m_pop:
        name = "High-Value Champions"
        badge = "Tier 1: High Value"
        color = "#2E5A44"  # deep sage forest
        description = "Customers who shop frequently, purchased recently, and generate higher recorded spending than the population median."
        characteristics = [
            f"Median spending of £{m_med:,.2f} ({(m_med/m_pop):.1f}x population median)",
            f"High purchase frequency of {f_med:.0f} orders (population median: {f_pop:.0f})",
            f"Strong recency ({r_med:.0f} days since last transaction)"
        ]
        business_insight = "Prioritize VIP loyalty recognition, early product previews, and premium customer service to maintain high retention."

    elif r_med <= r_pop and f_med >= f_pop and m_med < m_pop:
        name = "Active Regular Shoppers"
        badge = "Tier 2: High Engagement"
        color = "#5A7D6B"  # soft muted sage
        description = "Engaged, regular shoppers who order consistently but maintain moderate order values per transaction."
        characteristics = [
            f"Purchased recently ({r_med:.0f} days ago)",
            f"Steady order cadence of {f_med:.0f} orders",
            f"Moderate recorded spend (£{m_med:,.2f})"
        ]
        business_insight = "Cross-selling related basket items or offering volume discounts may encourage higher average order values."

    elif r_med <= r_pop and f_med < f_pop:
        name = "Promising Recent Shoppers"
        badge = "Tier 3: Emerging"
        color = "#C77D5C"  # terracotta accent
        description = "Recently active customers with lower overall historical order counts, showing early engagement potential."
        characteristics = [
            f"Recent transaction activity ({r_med:.0f} days ago)",
            f"Low to moderate order count ({f_med:.0f} orders)",
            f"Entry-level spending (£{m_med:,.2f})"
        ]
        business_insight = "Onboarding sequences and prompt follow-up offers can convert these recent buyers into repeat loyalists."

    elif r_med > r_pop and (m_med >= m_pop or f_med >= f_pop):
        name = "At-Risk Valuable Shoppers"
        badge = "Tier 4: Retention Focus"
        color = "#8A6D3B"  # warm bronze
        description = "Shoppers who previously generated notable revenue or orders but haven't made a purchase in a prolonged period."
        characteristics = [
            f"High recency gap ({r_med:.0f} days inactive)",
            f"Historical spending of £{m_med:,.2f}",
            f"Demonstrated willingness to place multiple orders ({f_med:.0f} orders)"
        ]
        business_insight = "Win-back email campaigns with personalized incentives could reactivate interest before permanent attrition occurs."

    else:
        name = "Dormant Low-Engagement Shoppers"
        badge = "Tier 5: Low Engagement"
        color = "#7A8288"  # slate gray
        description = "Infrequent shoppers with long periods of inactivity and low cumulative monetary spend."
        characteristics = [
            f"Protracted inactivity ({r_med:.0f} days since last order)",
            f"Single or very few purchases ({f_med:.0f} orders)",
            f"Low recorded expenditure (£{m_med:,.2f})"
        ]
        business_insight = "Evaluate cost-effective automated re-engagement or reserve marketing budget for higher-converting segments."

    return {
        "cluster_id": cluster_id,
        "name": name,
        "badge": badge,
        "color": color,
        "description": description,
        "characteristics": characteristics,
        "business_insight": business_insight,
        "r_diff": r_diff,
        "f_diff": f_diff,
        "m_diff": m_diff
    }

def train_and_evaluate():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading RFM data from {PROCESSED_DATA_PATH}...")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    n_customers = len(df)
    print(f"Loaded {n_customers:,} customers.")

    features = ["Recency", "Frequency", "Monetary"]
    X_raw = df[features].values
    # Log1p transformation
    if not np.isfinite(X_raw).all() or (X_raw < 0).any():
        raise ValueError("RFM must contain finite non-negative features")
    X_log = np.log1p(X_raw)

    # Scalers
    scaler_raw = StandardScaler()
    X_raw_scaled = scaler_raw.fit_transform(X_raw)

    scaler_log = StandardScaler()
    X_log_scaled = scaler_log.fit_transform(X_log)

    # -------------------------------------------------------------
    # Experiment A vs Experiment B (K=2..8)
    # -------------------------------------------------------------
    candidate_k = list(range(2, 9))
    results_exp_a = []
    results_exp_b = []

    print("\n--- Evaluating Candidate K Values (K=2..8) ---")
    for k in candidate_k:
        # Experiment A: Raw Scaled
        km_a = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels_a = km_a.fit_predict(X_raw_scaled)
        sil_a = float(silhouette_score(X_raw_scaled, labels_a, random_state=42))
        db_a = float(davies_bouldin_score(X_raw_scaled, labels_a))
        ch_a = float(calinski_harabasz_score(X_raw_scaled, labels_a))
        sizes_a = [int(s) for s in np.bincount(labels_a)]
        min_pct_a = (min(sizes_a) / n_customers) * 100

        results_exp_a.append({
            "k": k,
            "inertia": round(float(km_a.inertia_), 2),
            "silhouette": round(sil_a, 4),
            "davies_bouldin": round(db_a, 4),
            "calinski_harabasz": round(ch_a, 2),
            "cluster_sizes": sizes_a,
            "min_cluster_pct": round(min_pct_a, 2)
        })

        # Experiment B: Log-Transformed Scaled
        km_b = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels_b = km_b.fit_predict(X_log_scaled)
        sil_b = float(silhouette_score(X_log_scaled, labels_b, random_state=42))
        db_b = float(davies_bouldin_score(X_log_scaled, labels_b))
        ch_b = float(calinski_harabasz_score(X_log_scaled, labels_b))
        sizes_b = [int(s) for s in np.bincount(labels_b)]
        min_pct_b = (min(sizes_b) / n_customers) * 100

        results_exp_b.append({
            "k": k,
            "inertia": round(float(km_b.inertia_), 2),
            "silhouette": round(sil_b, 4),
            "davies_bouldin": round(db_b, 4),
            "calinski_harabasz": round(ch_b, 2),
            "cluster_sizes": sizes_b,
            "min_cluster_pct": round(min_pct_b, 2)
        })

        print(f"K={k} | Raw Sil: {sil_a:.4f} (Min%: {min_pct_a:.1f}%) | Log Sil: {sil_b:.4f} (Min%: {min_pct_b:.1f}%)")

    # Documented K Selection Strategy:
    # We analyze silhouette score, Davies-Bouldin index, inertia elbow, and cluster size balance.
    # On raw RFM, extreme spenders form small clusters containing < 1% of customers.
    # In Experiment B (log1p), distributions are balanced.
    # Among candidate K values, K=4 (or K=3) offers high silhouette, distinct operational business profiles,
    # and no degenerate clusters (all clusters > 10% of dataset).
    # Let's inspect K=4 in Experiment B as the chosen standard.
    selected_k = 4
    print(f"\n[SELECTION] Selected K = {selected_k} for the primary model.")

    # K=4 is an interpretability choice, not the global silhouette optimum.
    # Refit with exactly the candidate settings so evaluation and final artifacts agree.
    # Train final model on selected K with Log-Transformed Scaled features
    final_kmeans = KMeans(n_clusters=selected_k, random_state=42, n_init=20)
    final_labels = final_kmeans.fit_predict(X_log_scaled)
    df["Cluster"] = final_labels

    # Compute PCA (2 components) for 2D visualization
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_log_scaled)
    df["PCA1"] = np.round(X_pca[:, 0], 4)
    df["PCA2"] = np.round(X_pca[:, 1], 4)
    explained_var = [round(float(v), 4) for v in pca.explained_variance_ratio_]
    total_var = round(float(sum(pca.explained_variance_ratio_) * 100), 2)
    print(f"PCA 2D projection explained variance: {explained_var} (Total: {total_var}%)")

    # Final metrics for selected K in Experiment B
    final_sil = float(silhouette_score(X_log_scaled, final_labels, random_state=42))
    final_db = float(davies_bouldin_score(X_log_scaled, final_labels))
    final_ch = float(calinski_harabasz_score(X_log_scaled, final_labels))
    final_inertia = float(final_kmeans.inertia_)

    # Population Medians
    pop_medians = {
        "Recency": float(df["Recency"].median()),
        "Frequency": float(df["Frequency"].median()),
        "Monetary": round(float(df["Monetary"].median()), 2)
    }
    pop_means = {
        "Recency": round(float(df["Recency"].mean()), 2),
        "Frequency": round(float(df["Frequency"].mean()), 2),
        "Monetary": round(float(df["Monetary"].mean()), 2)
    }

    # Cluster Profiles
    profiles = []
    cluster_stats_list = []
    for cid in range(selected_k):
        cdf = df[df["Cluster"] == cid]
        count = len(cdf)
        pct = round((count / n_customers) * 100, 2)
        
        stat = {
            "cluster_id": cid,
            "count": int(count),
            "percentage": pct,
            "Recency_median": float(cdf["Recency"].median()),
            "Recency_mean": round(float(cdf["Recency"].mean()), 2),
            "Frequency_median": float(cdf["Frequency"].median()),
            "Frequency_mean": round(float(cdf["Frequency"].mean()), 2),
            "Monetary_median": round(float(cdf["Monetary"].median()), 2),
            "Monetary_mean": round(float(cdf["Monetary"].mean()), 2)
        }
        cluster_stats_list.append(stat)
        profile_meta = generate_personality_profile(cid, stat, pop_medians)
        profile_full = {**stat, **profile_meta}
        profiles.append(profile_full)

    # Sort profiles logically by descending Monetary median for clean presentation
    profiles.sort(key=lambda p: p["Monetary_median"], reverse=True)
    for rank, p in enumerate(profiles, start=1):
        p["display_rank"] = rank

    # Evaluation artifacts dictionary
    evaluation_summary = {
        "random_seed": 42,
        "n_init": 20,
        "silhouette_sample_size": n_customers,
        "sklearn_version": sklearn.__version__,
        "selection_reason": "K=4 is a descriptive granularity choice after inspecting K=2..8. K=2 has the highest log-space silhouette; four clusters retain useful RFM detail with balanced groups. The elbow is gradual, and no uniquely optimal K is claimed.",
        "training_ranges": {feature: {"min": float(df[feature].min()), "max": float(df[feature].max())} for feature in features},
        "selected_k": selected_k,
        "n_customers": n_customers,
        "silhouette_score": round(final_sil, 4),
        "davies_bouldin_index": round(final_db, 4),
        "calinski_harabasz_score": round(final_ch, 2),
        "inertia": round(final_inertia, 2),
        "pca_explained_variance_ratio": explained_var,
        "pca_total_variance_pct": total_var,
        "population_medians": pop_medians,
        "population_means": pop_means,
        "candidate_k_evaluation": results_exp_b
    }

    experiment_comparison = {
        "experiment_a_raw": {
            "name": "Experiment A: Raw RFM with Standard Scaling",
            "description": "StandardScaler applied directly to raw RFM values without log transformation.",
            "results": results_exp_a,
            "finding": "Raw scaling gives high silhouette values but concentrates small groups of extreme buyers. These groups may be valid outliers, but offer limited detail for typical customers."
        },
        "experiment_b_log": {
            "name": "Experiment B: Log-Transformed RFM with Standard Scaling",
            "description": "log1p applied to RFM features prior to StandardScaler, handling heavy right-tailed skewness.",
            "results": results_exp_b,
            "finding": "Log scaling compresses large values and produces more balanced descriptive groups. This is a change of geometry, not proof of higher accuracy or temporal stability."
        }
    }

    # Save models & artifacts
    pipeline = Pipeline([("log1p", FunctionTransformer(np.log1p)), ("scaler", scaler_log), ("kmeans", final_kmeans)])
    joblib.dump(pipeline, ARTIFACTS_DIR / "prediction_pipeline.joblib")
    joblib.dump(final_kmeans, ARTIFACTS_DIR / "kmeans_model.joblib")
    joblib.dump(scaler_log, ARTIFACTS_DIR / "scaler.joblib")
    joblib.dump(pca, ARTIFACTS_DIR / "pca_model.joblib")

    with open(ARTIFACTS_DIR / "cluster_profiles.json", "w") as f:
        json.dump(profiles, f, indent=2)

    with open(ARTIFACTS_DIR / "evaluation_metrics.json", "w") as f:
        json.dump(evaluation_summary, f, indent=2)

    with open(ARTIFACTS_DIR / "experiment_comparison.json", "w") as f:
        json.dump(experiment_comparison, f, indent=2)

    # Save customer segments CSV (with PCA coordinates for UI scatter plot)
    df.to_csv(ARTIFACTS_DIR / "customer_segments.csv", index=False)

    print(f"[SUCCESS] Artifacts saved to {ARTIFACTS_DIR}")

    # Generate Figures
    generate_figures(candidate_k, results_exp_a, results_exp_b, selected_k, df, profiles)

    return evaluation_summary, profiles

def generate_figures(candidate_k, results_a, results_b, selected_k, df, profiles):
    """Generates high-resolution academic figures for the report and UI."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]

    # 1. Elbow Plot (Inertia vs K)
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    inertias_b = [r["inertia"] for r in results_b]
    ax.plot(candidate_k, inertias_b, marker="o", color="#242725", linewidth=2, markersize=6, label="Inertia (Exp B)")
    ax.axvline(x=selected_k, color="#C77D5C", linestyle="--", linewidth=1.5, label=f"Selected K = {selected_k}")
    ax.set_title("Elbow Curve for Optimal Cluster Selection (K=2 to 8)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Number of Clusters (K)", fontsize=10)
    ax.set_ylabel("Inertia (Within-Cluster Sum of Squares)", fontsize=10)
    ax.set_xticks(candidate_k)
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "elbow_curve.png")
    plt.close()

    # 2. Silhouette Score vs K (Exp A vs Exp B)
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    sils_a = [r["silhouette"] for r in results_a]
    sils_b = [r["silhouette"] for r in results_b]
    ax.plot(candidate_k, sils_b, marker="s", color="#718776", linewidth=2, markersize=6, label="Exp B (Log-Transformed)")
    ax.plot(candidate_k, sils_a, marker="^", color="#A0A0A0", linestyle=":", linewidth=1.8, markersize=6, label="Exp A (Raw RFM)")
    ax.axvline(x=selected_k, color="#C77D5C", linestyle="--", linewidth=1.5, label=f"Selected K = {selected_k}")
    ax.set_title("Silhouette Score Comparison Across Candidate K Values", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Number of Clusters (K)", fontsize=10)
    ax.set_ylabel("Mean Silhouette Coefficient", fontsize=10)
    ax.set_xticks(candidate_k)
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "silhouette_scores.png")
    plt.close()

    # 3. PCA 2D Cluster Projection
    fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
    # Color palette
    color_map = {p["cluster_id"]: p["color"] for p in profiles}
    name_map = {p["cluster_id"]: p["name"] for p in profiles}
    
    for cid in range(selected_k):
        sub = df[df["Cluster"] == cid]
        ax.scatter(sub["PCA1"], sub["PCA2"], c=color_map.get(cid, "#555"), 
                   label=f"{name_map.get(cid, f'Cluster {cid}')} (n={len(sub):,})", 
                   alpha=0.6, s=18, edgecolors="none")

    ax.set_title("Two-Dimensional PCA Projection of Discovered Customer Clusters", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Principal Component 1", fontsize=10)
    ax.set_ylabel("Principal Component 2", fontsize=10)
    ax.legend(frameon=True, fontsize=8.5, loc="upper right")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pca_clusters.png")
    plt.close()

    # 4. Cluster Population Distribution
    fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
    sorted_profiles = sorted(profiles, key=lambda x: x["count"], reverse=True)
    names = [p["name"] for p in sorted_profiles]
    counts = [p["count"] for p in sorted_profiles]
    pcts = [p["percentage"] for p in sorted_profiles]
    colors = [p["color"] for p in sorted_profiles]

    bars = ax.barh(names, counts, color=colors, height=0.55)
    for bar, pct in zip(bars, pcts):
        ax.text(bar.get_width() + 40, bar.get_y() + bar.get_height()/2, f"{pct:.1f}%", 
                va="center", ha="left", fontsize=9, fontweight="bold", color="#242725")
    ax.set_xlim(0, max(counts) * 1.18)
    ax.set_title("Discovered Customer Segment Distribution", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Number of Customers", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "cluster_distribution.png")
    plt.close()

    # 5. Median RFM Comparison
    fig, axes = plt.subplots(1, 3, figsize=(11, 4), dpi=300)
    names_short = [p["name"].replace(" Shoppers", "").replace(" Customers", "") for p in profiles]
    colors_p = [p["color"] for p in profiles]

    # Recency
    r_meds = [p["Recency_median"] for p in profiles]
    axes[0].bar(names_short, r_meds, color=colors_p, width=0.55)
    axes[0].set_title("Median Recency (Days)\n[Lower = More Recent]", fontsize=10, fontweight="bold")
    axes[0].tick_params(axis='x', rotation=30, labelsize=8)

    # Frequency
    f_meds = [p["Frequency_median"] for p in profiles]
    axes[1].bar(names_short, f_meds, color=colors_p, width=0.55)
    axes[1].set_title("Median Frequency (Orders)\n[Higher = More Regular]", fontsize=10, fontweight="bold")
    axes[1].tick_params(axis='x', rotation=30, labelsize=8)

    # Monetary
    m_meds = [p["Monetary_median"] for p in profiles]
    axes[2].bar(names_short, m_meds, color=colors_p, width=0.55)
    axes[2].set_title("Median Monetary (£ GBP)\n[Higher = Higher Spend]", fontsize=10, fontweight="bold")
    axes[2].tick_params(axis='x', rotation=30, labelsize=8)

    plt.suptitle("RFM Behavioral Metrics Comparison Across Discovered Segments", fontsize=12, fontweight="bold", y=1.03)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rfm_comparison.png")
    plt.close()

    # 6. Experiment Comparison (Exp A vs Exp B Balance and Min Cluster Size)
    fig, ax = plt.subplots(figsize=(7, 4), dpi=300)
    min_pcts_a = [r["min_cluster_pct"] for r in results_a]
    min_pcts_b = [r["min_cluster_pct"] for r in results_b]
    ax.plot(candidate_k, min_pcts_b, marker="o", color="#718776", linewidth=2, label="Exp B (Log-Transformed): Balanced")
    ax.plot(candidate_k, min_pcts_a, marker="x", color="#C77D5C", linestyle="--", linewidth=1.8, label="Exp A (Raw RFM): Degenerate Outliers (<1%)")
    ax.set_title("Smallest Cluster Size (%) - Experiment A vs Experiment B", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Number of Clusters (K)", fontsize=10)
    ax.set_ylabel("Smallest Cluster Size (% of dataset)", fontsize=10)
    ax.set_xticks(candidate_k)
    ax.legend(frameon=True)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "experiment_comparison.png")
    plt.close()

    print(f"[SUCCESS] Exported high-resolution figures to {FIGURES_DIR}")

if __name__ == "__main__":
    with threadpool_limits(limits=1):
        train_and_evaluate()

