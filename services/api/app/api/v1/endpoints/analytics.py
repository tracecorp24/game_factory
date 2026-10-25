"""
Analytics & Reporting REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J & Module M12.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import PlainTextResponse

from services.api.app.modules.analytics.schemas import (
    AgentPerformanceMetrics,
    AnalyticsFilterParams,
    OverviewKPIs,
    QualityAnalytics,
    ReliabilityMetrics,
    TokenCostMetrics,
)
from services.api.app.modules.analytics.service import analytics_service

router = APIRouter(prefix="", tags=["Analytics & KPIs"])


def get_filters(
    project_id: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    workflow_version: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    agent: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> AnalyticsFilterParams:
    return AnalyticsFilterParams(
        project_id=project_id,
        campaign_id=campaign_id,
        workflow_version=workflow_version,
        model=model,
        agent=agent,
        status=status,
    )


@router.get("/analytics/overview", response_model=OverviewKPIs)
async def get_overview_kpis(filters: AnalyticsFilterParams = Depends(get_filters)):
    """High-level KPI overview across runs, spend, and quality."""
    return analytics_service.get_overview_kpis(filters)


@router.get("/analytics/costs", response_model=TokenCostMetrics)
async def get_token_costs(filters: AnalyticsFilterParams = Depends(get_filters)):
    """Token usage and cost analytics without double counting cached tokens."""
    return analytics_service.get_token_cost_metrics(filters)


@router.get("/analytics/agents", response_model=List[AgentPerformanceMetrics])
async def get_agent_performance(filters: AnalyticsFilterParams = Depends(get_filters)):
    """Per-agent task execution counts, retry rates, and measured p50/p95 latencies."""
    return analytics_service.get_agent_performance(filters)


@router.get("/analytics/artifacts")
async def get_artifact_analytics(filters: AnalyticsFilterParams = Depends(get_filters)):
    """Artifact production volumes, approval breakdown, and generation metrics."""
    overview = analytics_service.get_overview_kpis(filters)
    return {
        "total_artifacts": overview.total_artifacts,
        "approved_artifacts": overview.approved_artifacts,
        "cost_per_approved_artifact": overview.cost_per_approved_artifact,
    }


@router.get("/analytics/quality", response_model=QualityAnalytics)
async def get_quality_analytics(filters: AnalyticsFilterParams = Depends(get_filters)):
    """Gate pass rates, failure breakdown, and human review agreement stats."""
    return analytics_service.get_quality_analytics(filters)


@router.get("/analytics/reliability", response_model=ReliabilityMetrics)
async def get_reliability_metrics(filters: AnalyticsFilterParams = Depends(get_filters)):
    """Reliability indicators: SLO success rates, retry recovery, and idempotency diagnostics."""
    return analytics_service.get_reliability_metrics(filters)


@router.get("/analytics/export")
async def export_analytics(
    format: str = Query(default="csv", pattern="^(csv|jsonl)$"),
    filters: AnalyticsFilterParams = Depends(get_filters),
):
    """Export analytics rollups as CSV or JSONL format."""
    exported = analytics_service.export_data(format_type=format, filters=filters)
    media_type = "text/csv" if format == "csv" else "application/x-ndjson"
    filename = f"analytics_export.{format}"
    return Response(
        content=exported,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
