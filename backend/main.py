"""
ShopSense - FastAPI Backend Service
Academic Case Study API for Discovering Shopping Personalities
"""

import os
from fastapi import FastAPI, HTTPException, status, Query, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

from backend.schemas import (
    DatasetOverview,
    SegmentProfile,
    EvaluationResponse,
    VisualizationResponse,
    PredictRequest,
    PredictResponse
)
from backend.schemas import HealthResponse
from backend.services.data_service import data_service
from backend.services.clustering_service import clustering_service
from backend.services.prediction_service import prediction_service

app = FastAPI(
    title="ShopSense Analytics API",
    description="Customer Segmentation & Shopping Personality Discovery using K-Means and RFM Analysis",
    version="1.0.0"
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins if origin.strip()],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(FileNotFoundError)
async def missing_artifact(request: Request, exc: FileNotFoundError):
    return JSONResponse(status_code=503, content={"detail": "Required artifacts unavailable. Run preprocessing and training first."})

@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    # Avoid echoing non-finite inputs, which cannot be encoded as valid JSON.
    errors = [{key: error[key] for key in ("loc", "msg", "type")} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})

@app.get("/api/health", response_model=HealthResponse, summary="Service Health Check")
def health_check():
    data_service.get_overview()
    clustering_service.get_evaluation()
    clustering_service.get_visualization(sample_limit=1)
    prediction_service.predict(12, 6, 1800)
    return {
        "status": "healthy",
        "service": "ShopSense AI Backend",
        "dataset": "UCI Online Retail (ID 352)"
    }

@app.get("/api/overview", response_model=DatasetOverview, summary="Dataset & Preprocessing Summary")
def get_overview():
    try:
        return data_service.get_overview()
    except FileNotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Artifact data could not be processed.") from e

@app.get("/api/segments", response_model=List[SegmentProfile], summary="Discovered Shopping Personality Segments")
def get_segments():
    try:
        return clustering_service.get_segments()
    except FileNotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Artifact data could not be processed.") from e

@app.get("/api/segments/{cluster_id}", response_model=SegmentProfile, summary="Individual Segment Details")
def get_segment(cluster_id: int):
    segment = clustering_service.get_segment_by_id(cluster_id)
    if not segment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Segment with cluster ID {cluster_id} not found."
        )
    return segment

@app.get("/api/evaluation", response_model=EvaluationResponse, summary="Clustering Metrics and Experiment Comparison")
def get_evaluation():
    try:
        return clustering_service.get_evaluation()
    except FileNotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Artifact data could not be processed.") from e

@app.get("/api/visualization", response_model=VisualizationResponse, summary="PCA 2D Coordinates for Cluster Visualization")
def get_visualization(sample_limit: int = Query(5000, ge=1, le=10000)):
    try:
        return clustering_service.get_visualization(sample_limit=sample_limit)
    except FileNotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Artifact data could not be processed.") from e

@app.post("/api/predict", response_model=PredictResponse, summary="Predict Customer Shopping Personality")
def predict_personality(payload: PredictRequest):
    try:
        return prediction_service.predict(
            recency=payload.recency,
            frequency=payload.frequency,
            monetary=payload.monetary
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Artifact data could not be processed.") from e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

