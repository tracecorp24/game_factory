"""
Pydantic schemas and KPI models for Analytics & Reporting Dashboard.
CreativeForge Intelligence Studio v3.0 - Module M12.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyticsFilterParams(BaseModel):
    """Filters applicable across all analytics dashboards."""
    project_id: Optional[str] = None
    campaign_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    workflow_version: Optional[str] = None
    model: Optional[str] = None
    agent: Optional[str] = None
    status: Optional[str] = None


class OverviewKPIs(BaseModel):
    """Overview dashboard KPIs calculated conforming to Master Plan Section M12."""
    total_runs: int = 0
    completed_runs: int = 0
    failed_runs: int = 0
    cancelled_runs: int = 0
    terminal_runs: int = 0
    run_success_rate: Optional[float] = Field(
        default=None, description="completed_runs / terminal_runs. Null if terminal_runs is 0."
    )
    total_artifacts: int = 0
    approved_artifacts: int = 0
    qa_pass_rate: Optional[float] = Field(
        default=None, description="passed_gate_executions / all_final_gate_executions. Null if 0."
    )
    node_retry_rate: Optional[float] = Field(
        default=None, description="retried_node_executions / all_node_executions. Null if 0."
    )
    total_known_spend: float = Field(default=0.0, description="Sum of confirmed cost entries.")
    cost_per_approved_artifact: Optional[float] = Field(
        default=None, description="total_known_spend / approved_artifacts. Null if 0 approved."
    )
    unpriced_invocations: int = Field(default=0, description="Count of model calls without confirmed price catalog.")
    unpriced_call_ratio: Optional[float] = Field(
        default=None, description="unpriced_invocations / total_invocations. Never coerced to 0."
    )


class TokenCostMetrics(BaseModel):
    """Token & Cost breakdown avoiding double-counting and separating estimates."""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    total_billable_tokens: int = Field(
        default=0,
        description="input + output tokens without duplicate counting of cached tokens."
    )
    provider_reported_tokens: int = 0
    estimated_tokens: int = 0
    estimated_token_share: Optional[float] = None
    known_cost: float = 0.0
    unpriced_calls_count: int = 0
    currency: str = "USD"
    cost_by_model: List[Dict[str, Any]] = Field(default_factory=list)
    cost_by_kind: Dict[str, float] = Field(default_factory=dict)


class AgentPerformanceMetrics(BaseModel):
    """Per-agent execution, latency, and retry metrics."""
    agent_id: str
    task_count: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    retried_tasks: int = 0
    success_rate: Optional[float] = None
    node_retry_rate: Optional[float] = None
    p50_latency_ms: Optional[float] = None
    p95_latency_ms: Optional[float] = None
    avg_tokens_per_task: Optional[float] = None
    total_cost: float = 0.0


class QualityAnalytics(BaseModel):
    """Quality gate pass rates, rubric score distributions, and reviewer agreement."""
    total_evaluations: int = 0
    passed_evaluations: int = 0
    failed_evaluations: int = 0
    needs_review_count: int = 0
    qa_pass_rate: Optional[float] = None
    avg_rubric_score: Optional[float] = None
    gate_failure_breakdown: Dict[str, int] = Field(default_factory=dict)
    human_approved_count: int = 0
    human_rejected_count: int = 0
    human_approval_rate: Optional[float] = None


class ReliabilityMetrics(BaseModel):
    """System reliability, SLO tracking, and idempotency diagnostics."""
    total_runs: int = 0
    slo_success_rate: Optional[float] = None
    node_retry_rate: Optional[float] = None
    retry_attempts_total: int = 0
    p95_run_latency_sec: Optional[float] = None
    idempotency_duplicate_calls: int = 0
