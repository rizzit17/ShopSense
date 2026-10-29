import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from backend.services.prediction_service import prediction_service
from backend.services.clustering_service import clustering_service
from backend.services.data_service import data_service

def test_preprocessing_audit_exists():
    overview = data_service.get_overview()
    assert overview["total_customers"] == 4338
    assert overview["total_clean_rows"] == 392692
    assert overview["total_raw_rows"] == 541909
    assert overview["discovered_segments_count"] == 4
    assert overview["total_revenue_gbp"] > 8_000_000

def test_clustering_profiles_loaded():
    segments = clustering_service.get_segments()
    assert len(segments) == 4
    total_pct = sum(s["percentage"] for s in segments)
    assert 99.0 <= total_pct <= 101.0
    for s in segments:
        assert "name" in s
        assert "description" in s
        assert "Monetary_median" in s
        assert s["count"] > 500  # all clusters well-balanced (>10%)

def test_prediction_service_valid():
    # Customer with low recency, high frequency, high spend -> High-Value Champions
    res = prediction_service.predict(recency=5, frequency=15, monetary=5000.0)
    assert res["segment_name"] == "High-Value Champions"
    assert res["is_outlier"] is False

    # Dormant customer with high recency, 1 order, low spend -> Dormant Low-Engagement
    res2 = prediction_service.predict(recency=250, frequency=1, monetary=150.0)
    assert res2["segment_name"] == "Dormant Low-Engagement Shoppers"
    assert res2["is_outlier"] is False

def test_prediction_outlier_detection():
    # Extreme spending outside training range
    res = prediction_service.predict(recency=10, frequency=5, monetary=900000.0)
    assert res["is_outlier"] is True
    assert "exceeds" in res["outlier_warning"]

def test_pca_visualization_payload():
    viz = clustering_service.get_visualization(sample_limit=100)
    assert viz["total_points"] > 0
    assert len(viz["points"]) <= 100
    assert "pca1" in viz["points"][0]
    assert "pca2" in viz["points"][0]

