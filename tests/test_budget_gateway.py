"""Tests for BudgetGuard, ModelGateway, PriceCatalog, and Dynamic Fallback."""

import pytest
from services.api.app.modules.budgets import (
    BudgetBlockedException,
    BudgetGuard,
    CostKind,
    CostStatus,
    ModelCapability,
    ModelGateway,
    ModelGatewayRequest,
    ModelTier,
    PriceCatalog,
)


def test_budget_guard_limits_and_blocking():
    """Verifies that BudgetGuard alerts on soft limits and blocks hard limits."""
    guard = BudgetGuard()

    # Configure run budget: soft = $5.00, hard = $10.00
    guard.set_budget(
        scope_id="run_100",
        scope_type="run",
        soft_limit_usd=5.00,
        hard_limit_usd=10.00,
        current_spend_usd=3.00,
    )

    # 1. Under soft limit: spend $1.00 -> projected $4.00 -> OK, no warnings
    warnings = guard.check_budget_before_call(estimated_cost_usd=1.00, run_id="run_100")
    assert len(warnings) == 0

    # 2. Crosses soft limit: spend $3.00 -> projected $6.00 -> Warning issued, not blocked
    warnings = guard.check_budget_before_call(estimated_cost_usd=3.00, run_id="run_100")
    assert len(warnings) == 1
    assert warnings[0]["event_type"] == "BUDGET_SOFT_LIMIT_EXCEEDED"
    assert warnings[0]["projected_total_usd"] == 6.00

    # 3. Exceeds hard limit: spend $8.00 -> projected $11.00 -> Blocked!
    with pytest.raises(BudgetBlockedException) as exc_info:
        guard.check_budget_before_call(estimated_cost_usd=8.00, run_id="run_100")

    err = str(exc_info.value)
    assert "BUDGET_BLOCKED" in err
    assert "run_100" in err
    assert "$10.0000" in err


def test_token_pricing_non_double_counting_cached_tokens():
    """
    Verifies that cached input tokens are strictly isolated from billable
    uncached input tokens, preventing double charging.
    """
    # 1,000,000 total input tokens, of which 400,000 are cached
    # On gpt-4o: $2.50 per M input, $1.25 per M cached, $10.00 per M output
    total_cost, uncached_in, cached_in, out_cost = PriceCatalog.calculate_token_cost(
        model_id="gpt-4o",
        input_tokens=1_000_000,
        output_tokens=100_000,
        cached_tokens=400_000,
        provider_total_includes_cached=True,
    )

    # 600,000 uncached * $2.50 = $1.50
    # 400,000 cached * $1.25 = $0.50
    # 100,000 output * $10.00 = $1.00
    # Total = $3.00
    assert uncached_in == 1.50
    assert cached_in == 0.50
    assert out_cost == 1.00
    assert total_cost == 3.00


def test_media_pricing_unpriced_never_defaults_to_zero():
    """
    Master Plan requirement: Unknown external media calls must be flagged
    as 'unpriced' with amount None, NEVER coerced to $0.00!
    """
    # Known rate check
    known_cost, is_unpriced, status = PriceCatalog.calculate_media_cost("dall-e-3-hd", units=2)
    assert known_cost == 0.16
    assert is_unpriced is False
    assert status == CostStatus.ACTUAL

    # Unknown rate check
    unknown_cost, is_unpriced, status = PriceCatalog.calculate_media_cost("third_party_video_gen_v99", units=1)
    assert unknown_cost is None
    assert is_unpriced is True
    assert status == CostStatus.UNPRICED


@pytest.mark.asyncio
async def test_model_gateway_routing_and_execution():
    """Verifies that ModelGateway selects best candidate model and executes successfully."""
    gateway = ModelGateway()

    req = ModelGatewayRequest(
        messages=[{"role": "user", "content": "Write a Match-3 hook slogan"}],
        required_capabilities=[ModelCapability.TEXT, ModelCapability.STRUCTURED_OUTPUT],
        preferred_tier=ModelTier.FAST_LITE,
        run_id="run_gw_01",
    )

    resp = await gateway.execute(req)
    assert resp.model_used in ("gpt-4o-mini", "gemini-1.5-flash", "mock-fast-model")
    assert resp.fallback_used is False
    assert resp.token_usage.total_tokens > 0
    assert resp.cost_entry.amount is not None
    assert resp.cost_entry.amount > 0.0


@pytest.mark.asyncio
async def test_model_gateway_dynamic_fallback():
    """
    Verifies that when primary model encounters an error (rate limit / 5xx),
    ModelGateway dynamically fails over to an approved fallback model in the allowlist.
    """
    gateway = ModelGateway()

    req = ModelGatewayRequest(
        messages=[{"role": "user", "content": "Analyze game visual style"}],
        preferred_model="gpt-4o",  # Has fallback candidate 'claude-3-5-sonnet'
        simulate_provider_error=True,  # Triggers simulated 429
        run_id="run_fallback_01",
    )

    resp = await gateway.execute(req)
    assert resp.fallback_used is True
    assert resp.primary_model == "gpt-4o"
    assert resp.model_used in ("claude-3-5-sonnet", "gpt-4o-mini")
    assert "RateLimitExceeded" in str(resp.fallback_reason)
    assert resp.token_usage.total_tokens > 0
    assert resp.cost_entry.amount is not None


@pytest.mark.asyncio
async def test_model_gateway_blocks_when_budget_exceeded():
    """Verifies that ModelGateway blocks execution if the budget is exhausted."""
    guard = BudgetGuard()
    guard.set_budget(scope_id="proj_exhausted", scope_type="project", soft_limit_usd=1.00, hard_limit_usd=2.00, current_spend_usd=2.00)

    gateway = ModelGateway(budget_guard=guard)
    req = ModelGatewayRequest(
        messages=[{"role": "user", "content": "Hello world"}],
        project_id="proj_exhausted",
    )

    with pytest.raises(BudgetBlockedException) as exc_info:
        await gateway.execute(req)

    assert "BUDGET_BLOCKED" in str(exc_info.value)
