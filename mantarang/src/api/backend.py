"""
FastAPI Backend for ManTarang Music Recommendation System

Uses track_data_final.csv as the primary recommendation source.
"""

import time
import uuid
import pathlib
from typing import Dict, Optional
from contextlib import asynccontextmanager
import os
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ..services.csv_recommender import get_recommendations as csv_recommend, get_df
from ..utils.logging_config import setup_logging

# Bootstrap logging before anything else touches get_logger()
setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"), enable_console=True)

from .logging_middleware import LoggingMiddleware, PerformanceLoggingMiddleware

# Setup module logger
logger = logging.getLogger(__name__)

# Pre-warm the CSV dataset on import
_dataset_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    global _dataset_ready
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    logger.info("Loading track_data_final.csv dataset...")
    try:
        df = get_df()
        _dataset_ready = True
        logger.info(f"Dataset loaded: {len(df):,} tracks ready")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        _dataset_ready = False

    yield

    logger.info("ManTarang shutting down.")


# Create FastAPI app
app = FastAPI(
    title="ManTarang API",
    description="4-Agent Music Recommendation System with Strategic Planning",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware, exclude_paths=["/health", "/docs", "/openapi.json"])
app.add_middleware(PerformanceLoggingMiddleware, slow_request_threshold=5.0)


# Request/Response Models
class RecommendationRequest(BaseModel):
    """Request model for music recommendations."""
    query: str = Field(..., description="User's music preference query")
    session_id: Optional[str] = Field(
        None, 
        description="Session identifier for conversation history"
    )
    max_recommendations: int = Field(
        3, 
        ge=1, 
        le=10, 
        description="Maximum number of recommendations"
    )
    include_previews: bool = Field(
        True, 
        description="Whether to include audio previews"
    )
    chat_context: Optional[Dict] = Field(
        None,
        description="Previous chat context for continuity"
    )


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: float
    version: str
    components: Dict[str, str]


class PlanningResponse(BaseModel):
    """Response model for planning strategy."""
    strategy: Dict  # Using Dict instead of PlanningStrategy for now
    execution_time: float
    session_id: str


# API Endpoints

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        version="1.0.0",
        components={
            "csv_dataset": "active" if _dataset_ready else "loading",
            "recommendation_engine": "csv_based",
        }
    )


@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """Get music recommendations from track_data_final.csv."""
    start_time = time.time()
    logger.info(f"Recommendation request: '{request.query}'")

    try:
        result = csv_recommend(request.query, n=request.max_recommendations)
        processing_time = time.time() - start_time

        response_data = {
            "recommendations": result["recommendations"],
            "strategy_used": result["strategy_used"],
            "reasoning": result["reasoning"],
            "aggregate_metrics": result.get("aggregate_metrics", {}),
            "session_id": request.session_id or str(uuid.uuid4()),
            "processing_time": round(processing_time, 3),
            "metadata": {"source": "csv_dataset", "total_tracks": 8778},
        }

        logger.info(
            f"Returned {len(result['recommendations'])} tracks "
            f"(strategy={result['strategy_used'].get('strategy')}) "
            f"in {processing_time:.2f}s"
        )
        return JSONResponse(content=response_data)

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Recommendation error: {e}")
        return JSONResponse(
            content={
                "error": "Recommendation generation failed",
                "detail": str(e),
                "session_id": request.session_id,
                "processing_time": processing_time,
                "recommendations": [],
                "strategy_used": {},
                "reasoning": [f"Error: {str(e)}"],
                "metadata": {"error": True},
            },
            status_code=500,
        )


@app.post("/planning")
async def get_planning_strategy(request: RecommendationRequest):
    """Return a planning preview for the query (informational)."""
    start_time = time.time()
    strategy = {
        "task_analysis": {
            "primary_goal": f"Find music matching: {request.query}",
            "complexity_level": "medium",
            "context_factors": ["csv_dataset", "genre_mood_matching", "popularity_scoring"],
        },
        "coordination_strategy": {
            "genre_mood_agent": {"focus": "Genre/mood keyword extraction"},
            "discovery_agent": {"focus": "Artist & similarity matching"},
        },
        "evaluation_framework": {
            "primary_weights": {"popularity": 0.5, "genre_match": 0.3, "diversity": 0.2}
        },
    }
    return PlanningResponse(
        strategy=strategy,
        execution_time=round(time.time() - start_time, 3),
        session_id=request.session_id or str(uuid.uuid4()),
    )


@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Stub – session history not persisted in CSV mode."""
    return {"session_id": session_id, "history": [], "total_interactions": 0}


@app.get("/sessions/{session_id}/context")
async def get_session_context(session_id: str):
    """Stub – session context not persisted in CSV mode."""
    return {"session_id": session_id, "context_summary": {}, "timestamp": time.time()}


@app.post("/feedback")
async def submit_feedback(
    session_id: str,
    recommendation_id: str,
    feedback: str,
    background_tasks: BackgroundTasks,
):
    """Accept user feedback (logged only)."""
    if feedback not in ["thumbs_up", "thumbs_down"]:
        raise HTTPException(status_code=400, detail="Invalid feedback value")
    background_tasks.add_task(
        _log_feedback, session_id=session_id,
        recommendation_id=recommendation_id, feedback=feedback
    )
    return {"message": "Feedback submitted successfully"}


async def _log_feedback(session_id: str, recommendation_id: str, feedback: str):
    logger.info(f"Feedback: {feedback} | rec={recommendation_id} | session={session_id}")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": time.time(), "path": str(request.url)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": time.time(), "path": str(request.url)},
    )


# ── /api/* prefix router (used in production where FastAPI serves React) ──────
_api = APIRouter(prefix="/api")
_api.add_api_route("/recommendations", get_recommendations, methods=["POST"])
_api.add_api_route("/health",          health_check,        methods=["GET"])
app.include_router(_api)

# ── Serve React build if dist/ exists (production / HuggingFace Spaces) ───────
_DIST = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "dist"
if _DIST.exists():
    _assets = _DIST / "assets"
    if _assets.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def _spa_fallback(full_path: str = ""):
        candidate = _DIST / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(_DIST / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)