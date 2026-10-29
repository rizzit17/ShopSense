import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_api_overview():
    res = client.get("/api/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_customers"] == 4338
    assert len(data["cleaning_steps"]) == 4

def test_api_segments():
    res = client.get("/api/segments")
    assert res.status_code == 200
    segments = res.json()
    assert len(segments) == 4
    first_id = segments[0]["cluster_id"]

    res_single = client.get(f"/api/segments/{first_id}")
    assert res_single.status_code == 200
    assert res_single.json()["cluster_id"] == first_id

def test_api_segment_not_found():
    res = client.get("/api/segments/999")
    assert res.status_code == 404

def test_api_evaluation():
    res = client.get("/api/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert data["selected_k"] == 4
    assert "candidate_k_evaluation" in data
    assert len(data["candidate_k_evaluation"]) == 7

def test_api_visualization():
    res = client.get("/api/visualization?sample_limit=200")
    assert res.status_code == 200
    data = res.json()
    assert data["total_points"] <= 200
    assert "pca_variance_pct" in data

def test_api_predict_valid():
    payload = {
        "recency": 12.0,
        "frequency": 8,
        "monetary": 2500.0
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "segment_name" in data
    assert "comparison" in data

def test_api_predict_invalid_inputs():
    # Negative recency
    res1 = client.post("/api/predict", json={"recency": -5, "frequency": 1, "monetary": 100})
    assert res1.status_code == 422

    # Zero frequency
    res2 = client.post("/api/predict", json={"recency": 10, "frequency": 0, "monetary": 100})
    assert res2.status_code == 422

    # Negative monetary
    res3 = client.post("/api/predict", json={"recency": 10, "frequency": 1, "monetary": -50})
    assert res3.status_code == 422

