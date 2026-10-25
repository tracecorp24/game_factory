"""
Main FastAPI Application Gateway for CreativeForge Intelligence Studio v3.0.
Responsible for REST API routing, CORS, Lifespan initialization, and OpenAPI documentation.
CreativeForge Intelligence Studio v3.0 - Section J & Prompt 5.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from services.api.app.api.v1.router import api_v1_router
from services.api.app.modules.analytics.service import analytics_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("creativeforge.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager initializing shared services and seed data."""
    logger.info("Starting CreativeForge Intelligence Studio v3.0 API Gateway...")
    # Initialize analytics demo baseline
    analytics_service.seed_demo_data()
    yield
    logger.info("Shutting down CreativeForge API Gateway...")


app = FastAPI(
    title="CreativeForge Intelligence Studio v3.0 API",
    description=(
        "Production REST and Server-Sent Events (SSE) API Gateway for CreativeForge. "
        "Provides endpoints for Projects, Trend Intelligence, Game DNA, Hypotheses, "
        "Workflows, Runs, Event Ledger, Model Telemetry, Artifacts, 7 Quality Gates, and Analytics."
    ),
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for Next.js frontend (Agent 6)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*",  # Permissive in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Last-Event-ID", "Content-Disposition"],
)


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Global system health probe."""
    return {
        "status": "healthy",
        "service": "creativeforge-api",
        "version": "3.0.0",
        "quality_gates_engine": "online",
        "sse_relay_hub": "online",
    }


# Mount API v1 router
app.include_router(api_v1_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all unhandled exception handler returning structured JSON."""
    logger.error(f"Unhandled exception at {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": str(exc),
            "path": request.url.path,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.api.app.main:app", host="0.0.0.0", port=8000, reload=True)
