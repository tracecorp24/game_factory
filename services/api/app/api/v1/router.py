"""
API v1 Router aggregating all domain sub-routers.
CreativeForge Intelligence Studio v3.0 - Section J.
"""

from fastapi import APIRouter

from services.api.app.api.v1.endpoints import (
    admin,
    analytics,
    artifacts,
    attempts,
    compare,
    concepts,
    events,
    experiments,
    games,
    model_calls,
    projects,
    runs,
    trends,
    workflows,
    comfy,
)

api_v1_router = APIRouter()

api_v1_router.include_router(projects.router)
api_v1_router.include_router(trends.router)
api_v1_router.include_router(games.router)
api_v1_router.include_router(concepts.router)
api_v1_router.include_router(workflows.router)
api_v1_router.include_router(runs.router)
api_v1_router.include_router(events.router)
api_v1_router.include_router(model_calls.router)
api_v1_router.include_router(attempts.router)
api_v1_router.include_router(artifacts.router)
api_v1_router.include_router(experiments.router)
api_v1_router.include_router(analytics.router)
api_v1_router.include_router(compare.router)
api_v1_router.include_router(admin.router)
api_v1_router.include_router(comfy.router, prefix="/comfy")
