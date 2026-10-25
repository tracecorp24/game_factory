"""
Unit tests for Analytics & Reporting Engine KPI computations.
Validates acceptance criteria: zero division returns null, cache tokens are not double-counted.
CreativeForge Intelligence Studio v3.0 - Module M12.
"""

import json
import pytest
from services.api.app.modules.analytics.schemas import AnalyticsFilterParams
from services.api.app.modules.analytics.service import AnalyticsService


def test_zero_division_safety():
    """
    CRITICAL ACCEPTANCE CRITERION:
    When counts are 0, rates and cost ratios must return None (null in JSON), never crash or return 0.
    """
    empty_service = AnalyticsService()
    filters = AnalyticsFilterParams()

    overview = empty_service.get_overview_kpis(filters)
    assert overview.total_runs == 0
    assert overview.terminal_runs == 0
    assert overview.run_success_rate is None  # Must be null, not 0.0!
    assert overview.approved_artifacts == 0
    assert overview.cost_per_approved_artifact is None  # Must be null!
    assert overview.unpriced_call_ratio is None  # Must be null!
    assert overview.qa_pass_rate is None  # Must be null!
    assert overview.node_retry_rate is None  # Must be null!


def test_cache_tokens_not_double_counted():
    """
    CRITICAL ACCEPTANCE CRITERION:
    Cached input tokens must not be double counted when calculating total billable tokens.
    """
    svc = AnalyticsService()
    svc.record_model_invocation(
        {
            "id": "mi_test",
            "model": "gpt-4o",
            "input_tokens": 1000,
            "output_tokens": 300,
            "cached_tokens": 400,  # 400 of the 1000 input tokens were cached
            "usage_source": "provider_reported",
            "cost_amount": 0.010,
            "priced": True,
        }
    )

    metrics = svc.get_token_cost_metrics(AnalyticsFilterParams())
    assert metrics.input_tokens == 1000
    assert metrics.output_tokens == 300
    assert metrics.cached_tokens == 400
    # Billable tokens = 1000 + 300 = 1300. NOT 1000 + 300 + 400 (1700)!
    assert metrics.total_billable_tokens == 1300


def test_unpriced_invocations_never_zeroed():
    """
    CRITICAL ACCEPTANCE CRITERION:
    Calls without price catalog entries must be reported as unpriced/unknown, never coerced to $0.00.
    """
    svc = AnalyticsService()
    # Call 1: priced
    svc.record_model_invocation(
        {
            "id": "mi_1",
            "model": "gpt-4o",
            "input_tokens": 500,
            "output_tokens": 100,
            "cost_amount": 0.005,
            "priced": True,
        }
    )
    # Call 2: unpriced self-hosted / novel model
    svc.record_model_invocation(
        {
            "id": "mi_2",
            "model": "custom-finetune-v1",
            "input_tokens": 1000,
            "output_tokens": 500,
            "cost_amount": None,
            "priced": False,
        }
    )

    metrics = svc.get_token_cost_metrics(AnalyticsFilterParams())
    assert metrics.unpriced_calls_count == 1
    # Known cost only includes the priced call
    assert metrics.known_cost == 0.005

    overview = svc.get_overview_kpis(AnalyticsFilterParams())
    assert overview.unpriced_invocations == 1
    assert overview.unpriced_call_ratio == 0.5  # 1 unpriced / 2 total


def test_agent_latencies_and_retry_rate():
    svc = AnalyticsService()
    svc.record_node_execution(
        {"id": "n1", "agent_id": "agent_test", "retried": False, "duration_ms": 100.0}
    )
    svc.record_node_execution(
        {"id": "n2", "agent_id": "agent_test", "retried": True, "duration_ms": 200.0}
    )
    svc.record_node_execution(
        {"id": "n3", "agent_id": "agent_test", "retried": False, "duration_ms": 300.0}
    )

    agents = svc.get_agent_performance(AnalyticsFilterParams())
    assert len(agents) == 1
    agent = agents[0]
    assert agent.task_count == 3
    assert agent.retried_tasks == 1
    assert agent.node_retry_rate == round(1 / 3, 4)
    assert agent.p50_latency_ms == 200.0
    assert agent.p95_latency_ms == 300.0


def test_csv_and_jsonl_export():
    svc = AnalyticsService()
    svc.seed_demo_data()

    # CSV export
    csv_data = svc.export_data("csv", AnalyticsFilterParams())
    assert "metric,value" in csv_data
    assert "total_runs" in csv_data

    # JSONL export
    jsonl_data = svc.export_data("jsonl", AnalyticsFilterParams())
    lines = jsonl_data.strip().split("\n")
    assert len(lines) > 0
    # Every line must be valid JSON
    for line in lines:
        parsed = json.loads(line)
        assert "id" in parsed
