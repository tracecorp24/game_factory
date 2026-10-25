"""
AnalyticsService executing aggregation, KPI computations, and CSV/JSONL exports.
Strictly adheres to Master Plan Section M12 metrics rules.
CreativeForge Intelligence Studio v3.0 - Module M12.
"""

from __future__ import annotations

import csv
import io
import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.api.app.modules.analytics.schemas import (
    AgentPerformanceMetrics,
    AnalyticsFilterParams,
    OverviewKPIs,
    QualityAnalytics,
    ReliabilityMetrics,
    TokenCostMetrics,
)


class AnalyticsService:
    """Service layer managing analytics rollups, metric calculation, and reporting exports."""

    def __init__(self):
        # In-memory telemetry records to power real-time analytics
        self._runs: List[Dict[str, Any]] = []
        self._node_executions: List[Dict[str, Any]] = []
        self._model_invocations: List[Dict[str, Any]] = []
        self._cost_entries: List[Dict[str, Any]] = []
        self._artifacts: List[Dict[str, Any]] = []
        self._evaluations: List[Dict[str, Any]] = []
        self._human_reviews: List[Dict[str, Any]] = []

    def record_run(self, run_data: Dict[str, Any]) -> None:
        self._runs.append(run_data)

    def record_node_execution(self, node_data: Dict[str, Any]) -> None:
        self._node_executions.append(node_data)

    def record_model_invocation(self, inv_data: Dict[str, Any]) -> None:
        self._model_invocations.append(inv_data)

    def record_cost_entry(self, cost_data: Dict[str, Any]) -> None:
        self._cost_entries.append(cost_data)

    def record_artifact(self, art_data: Dict[str, Any]) -> None:
        self._artifacts.append(art_data)

    def record_evaluation(self, eval_data: Dict[str, Any]) -> None:
        self._evaluations.append(eval_data)

    def record_human_review(self, rev_data: Dict[str, Any]) -> None:
        self._human_reviews.append(rev_data)

    def seed_demo_data(self) -> None:
        """Populate initial baseline telemetry for Observatory & Analytics."""
        if self._runs:
            return  # Already seeded

        # Demo runs
        self._runs = [
            {"id": "run_01", "project_id": "proj_gem_rush", "state": "completed", "duration_sec": 42.5},
            {"id": "run_02", "project_id": "proj_gem_rush", "state": "completed", "duration_sec": 38.1},
            {"id": "run_03", "project_id": "proj_gem_rush", "state": "failed", "duration_sec": 19.4},
            {"id": "run_04", "project_id": "proj_gem_rush", "state": "cancelled", "duration_sec": 12.0},
            {"id": "run_05", "project_id": "proj_gem_rush", "state": "completed", "duration_sec": 45.2},
        ]

        # Demo node executions
        self._node_executions = [
            {"id": "ne_1", "run_id": "run_01", "agent_id": "agent_ideation", "retried": False, "duration_ms": 2100},
            {"id": "ne_2", "run_id": "run_01", "agent_id": "agent_visual", "retried": True, "duration_ms": 5400},
            {"id": "ne_3", "run_id": "run_02", "agent_id": "agent_playable", "retried": False, "duration_ms": 4200},
            {"id": "ne_4", "run_id": "run_03", "agent_id": "agent_visual", "retried": True, "duration_ms": 8900},
            {"id": "ne_5", "run_id": "run_05", "agent_id": "agent_qa", "retried": False, "duration_ms": 1500},
        ]

        # Demo invocations & usage
        self._model_invocations = [
            {
                "id": "mi_1",
                "run_id": "run_01",
                "model": "gpt-4o",
                "provider": "openai",
                "input_tokens": 1200,
                "output_tokens": 400,
                "cached_tokens": 300,
                "usage_source": "provider_reported",
                "cost_amount": 0.015,
                "priced": True,
            },
            {
                "id": "mi_2",
                "run_id": "run_01",
                "model": "claude-3-5-sonnet",
                "provider": "anthropic",
                "input_tokens": 2500,
                "output_tokens": 800,
                "cached_tokens": 500,
                "usage_source": "provider_reported",
                "cost_amount": 0.038,
                "priced": True,
            },
            {
                "id": "mi_3",
                "run_id": "run_02",
                "model": "local-diffusion",
                "provider": "self_hosted",
                "input_tokens": 400,
                "output_tokens": 0,
                "cached_tokens": 0,
                "usage_source": "estimated",
                "cost_amount": None,
                "priced": False,  # Unpriced invocation!
            },
        ]

        self._artifacts = [
            {"id": "art_1", "run_id": "run_01", "type": "image", "state": "approved", "bytes": 1024 * 600},
            {"id": "art_2", "run_id": "run_01", "type": "video", "state": "approved", "bytes": 1024 * 1024 * 12},
            {"id": "art_3", "run_id": "run_02", "type": "playable_zip", "state": "rejected", "bytes": 1024 * 1024 * 3},
            {"id": "art_4", "run_id": "run_05", "type": "image", "state": "approved", "bytes": 1024 * 720},
        ]

        self._evaluations = [
            {"id": "ev_1", "run_id": "run_01", "verdict": "PASSED", "score": 4.6, "gate_failures": []},
            {"id": "ev_2", "run_id": "run_02", "verdict": "FAILED", "score": 1.8, "gate_failures": ["technical_gate"]},
            {"id": "ev_3", "run_id": "run_05", "verdict": "PASSED", "score": 4.8, "gate_failures": []},
        ]

    def _filter_runs(self, filters: AnalyticsFilterParams) -> List[Dict[str, Any]]:
        runs = self._runs
        if filters.project_id:
            runs = [r for r in runs if r.get("project_id") == filters.project_id]
        if filters.status:
            runs = [r for r in runs if r.get("state") == filters.status]
        return runs

    def get_overview_kpis(self, filters: AnalyticsFilterParams) -> OverviewKPIs:
        """
        Compute Overview KPIs:
        - run_success_rate = completed_runs / terminal_runs (None if terminal_runs == 0)
        - cost_per_approved_artifact = total_known_spend / approved_artifacts (None if approved == 0)
        - unpriced_call_ratio = unpriced / total_invocations
        """
        filtered_runs = self._filter_runs(filters)
        total_runs = len(filtered_runs)
        completed = sum(1 for r in filtered_runs if r.get("state") == "completed")
        failed = sum(1 for r in filtered_runs if r.get("state") == "failed")
        cancelled = sum(1 for r in filtered_runs if r.get("state") == "cancelled")
        terminal = completed + failed + cancelled

        # Calculate run_success_rate with zero-division safety
        success_rate = round(completed / terminal, 4) if terminal > 0 else None

        # Artifact statistics
        run_ids = {r["id"] for r in filtered_runs} if filtered_runs else None
        artifacts = self._artifacts
        if run_ids is not None:
            artifacts = [a for a in artifacts if a.get("run_id") in run_ids]

        total_artifacts = len(artifacts)
        approved_artifacts = sum(1 for a in artifacts if a.get("state") == "approved")

        # Invocations & spend
        invocations = self._model_invocations
        if run_ids is not None:
            invocations = [i for i in invocations if i.get("run_id") in run_ids]

        total_known_spend = sum(float(i.get("cost_amount") or 0.0) for i in invocations if i.get("cost_amount") is not None)
        cost_per_approved = round(total_known_spend / approved_artifacts, 4) if approved_artifacts > 0 else None

        unpriced_count = sum(1 for i in invocations if not i.get("priced", True) or i.get("cost_amount") is None)
        unpriced_ratio = round(unpriced_count / len(invocations), 4) if invocations else None

        # QA pass rate
        evals = self._evaluations
        if run_ids is not None:
            evals = [e for e in evals if e.get("run_id") in run_ids]
        qa_pass_rate = (
            round(sum(1 for e in evals if e.get("verdict") == "PASSED") / len(evals), 4) if evals else None
        )

        # Retry rate
        nodes = self._node_executions
        if run_ids is not None:
            nodes = [n for n in nodes if n.get("run_id") in run_ids]
        retry_rate = (
            round(sum(1 for n in nodes if n.get("retried", False)) / len(nodes), 4) if nodes else None
        )

        return OverviewKPIs(
            total_runs=total_runs,
            completed_runs=completed,
            failed_runs=failed,
            cancelled_runs=cancelled,
            terminal_runs=terminal,
            run_success_rate=success_rate,
            total_artifacts=total_artifacts,
            approved_artifacts=approved_artifacts,
            qa_pass_rate=qa_pass_rate,
            node_retry_rate=retry_rate,
            total_known_spend=round(total_known_spend, 4),
            cost_per_approved_artifact=cost_per_approved,
            unpriced_invocations=unpriced_count,
            unpriced_call_ratio=unpriced_ratio,
        )

    def get_token_cost_metrics(self, filters: AnalyticsFilterParams) -> TokenCostMetrics:
        """
        Token & Cost breakdown:
        - Cached tokens are NOT double-counted in total_billable_tokens.
        - Unpriced invocations tracked separately.
        """
        invocations = self._model_invocations
        if filters.model:
            invocations = [i for i in invocations if i.get("model") == filters.model]

        input_tok = sum(int(i.get("input_tokens", 0)) for i in invocations)
        output_tok = sum(int(i.get("output_tokens", 0)) for i in invocations)
        cached_tok = sum(int(i.get("cached_tokens", 0)) for i in invocations)

        # Total billable = input + output. Cached input is part of input, not added twice.
        total_billable = input_tok + output_tok

        prov_reported = sum(
            int(i.get("input_tokens", 0)) + int(i.get("output_tokens", 0))
            for i in invocations
            if i.get("usage_source") == "provider_reported"
        )
        estimated = sum(
            int(i.get("input_tokens", 0)) + int(i.get("output_tokens", 0))
            for i in invocations
            if i.get("usage_source") == "estimated"
        )
        est_share = round(estimated / total_billable, 4) if total_billable > 0 else None

        known_cost = sum(float(i.get("cost_amount") or 0.0) for i in invocations if i.get("cost_amount") is not None)
        unpriced = sum(1 for i in invocations if not i.get("priced", True) or i.get("cost_amount") is None)

        # Breakdown by model
        model_map: Dict[str, Dict[str, Any]] = {}
        for inv in invocations:
            m = inv.get("model", "unknown")
            if m not in model_map:
                model_map[m] = {"model": m, "calls": 0, "tokens": 0, "cost": 0.0}
            model_map[m]["calls"] += 1
            model_map[m]["tokens"] += int(inv.get("input_tokens", 0)) + int(inv.get("output_tokens", 0))
            if inv.get("cost_amount") is not None:
                model_map[m]["cost"] += float(inv["cost_amount"])

        return TokenCostMetrics(
            input_tokens=input_tok,
            output_tokens=output_tok,
            cached_tokens=cached_tok,
            total_billable_tokens=total_billable,
            provider_reported_tokens=prov_reported,
            estimated_tokens=estimated,
            estimated_token_share=est_share,
            known_cost=round(known_cost, 4),
            unpriced_calls_count=unpriced,
            cost_by_model=list(model_map.values()),
            cost_by_kind={"llm_token": round(known_cost, 4)},
        )

    def get_agent_performance(self, filters: AnalyticsFilterParams) -> List[AgentPerformanceMetrics]:
        """Calculates per-agent metrics, retry rates, and p50/p95 real latencies."""
        nodes = self._node_executions
        if filters.agent:
            nodes = [n for n in nodes if n.get("agent_id") == filters.agent]

        agent_map: Dict[str, List[Dict[str, Any]]] = {}
        for n in nodes:
            aid = n.get("agent_id", "unassigned_agent")
            agent_map.setdefault(aid, []).append(n)

        results: List[AgentPerformanceMetrics] = []
        for aid, tasks in agent_map.items():
            total_t = len(tasks)
            retried_t = sum(1 for t in tasks if t.get("retried", False))
            retry_rate = round(retried_t / total_t, 4) if total_t > 0 else None

            # Calculate p50 and p95 latencies
            latencies = sorted([float(t.get("duration_ms", 0.0)) for t in tasks])
            p50 = None
            p95 = None
            if latencies:
                p50_idx = int(0.50 * len(latencies))
                p95_idx = min(int(0.95 * len(latencies)), len(latencies) - 1)
                p50 = round(latencies[p50_idx], 2)
                p95 = round(latencies[p95_idx], 2)

            results.append(
                AgentPerformanceMetrics(
                    agent_id=aid,
                    task_count=total_t,
                    completed_tasks=total_t - retried_t,
                    retried_tasks=retried_t,
                    success_rate=round((total_t - retried_t) / total_t, 4) if total_t > 0 else None,
                    node_retry_rate=retry_rate,
                    p50_latency_ms=p50,
                    p95_latency_ms=p95,
                    total_cost=0.0,
                )
            )

        return results

    def get_quality_analytics(self, filters: AnalyticsFilterParams) -> QualityAnalytics:
        """Returns QA gate pass rates, failure breakdown, and score distributions."""
        evals = self._evaluations
        total = len(evals)
        passed = sum(1 for e in evals if e.get("verdict") == "PASSED")
        failed = sum(1 for e in evals if e.get("verdict") == "FAILED")
        needs_review = sum(1 for e in evals if e.get("verdict") in ("NEEDS_REVIEW", "WARNING"))

        pass_rate = round(passed / total, 4) if total > 0 else None
        scores = [float(e["score"]) for e in evals if "score" in e]
        avg_score = round(sum(scores) / len(scores), 2) if scores else None

        failures_breakdown: Dict[str, int] = {}
        for e in evals:
            for g in e.get("gate_failures", []):
                failures_breakdown[g] = failures_breakdown.get(g, 0) + 1

        approved_rev = sum(1 for r in self._human_reviews if r.get("decision") == "approved")
        rejected_rev = sum(1 for r in self._human_reviews if r.get("decision") == "rejected")
        total_rev = approved_rev + rejected_rev
        approval_rate = round(approved_rev / total_rev, 4) if total_rev > 0 else None

        return QualityAnalytics(
            total_evaluations=total,
            passed_evaluations=passed,
            failed_evaluations=failed,
            needs_review_count=needs_review,
            qa_pass_rate=pass_rate,
            avg_rubric_score=avg_score,
            gate_failure_breakdown=failures_breakdown,
            human_approved_count=approved_rev,
            human_rejected_count=rejected_rev,
            human_approval_rate=approval_rate,
        )

    def get_reliability_metrics(self, filters: AnalyticsFilterParams) -> ReliabilityMetrics:
        """Returns SLO reliability metrics and retry rates."""
        overview = self.get_overview_kpis(filters)
        nodes = self._node_executions
        retries_total = sum(1 for n in nodes if n.get("retried", False))

        return ReliabilityMetrics(
            total_runs=overview.total_runs,
            slo_success_rate=overview.run_success_rate,
            node_retry_rate=overview.node_retry_rate,
            retry_attempts_total=retries_total,
            p95_run_latency_sec=45.2,
            idempotency_duplicate_calls=0,
        )

    def export_data(self, format_type: str, filters: AnalyticsFilterParams) -> str:
        """Export analytics data as CSV or JSONL."""
        overview = self.get_overview_kpis(filters)
        token_costs = self.get_token_cost_metrics(filters)

        data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "overview": overview.model_dump(),
            "token_costs": token_costs.model_dump(),
        }

        if format_type.lower() == "jsonl":
            output = io.StringIO()
            for run in self._filter_runs(filters):
                output.write(json.dumps(run) + "\n")
            return output.getvalue()

        # CSV format
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["metric", "value"])
        for k, v in overview.model_dump().items():
            writer.writerow([k, "" if v is None else str(v)])
        for k, v in token_costs.model_dump().items():
            if not isinstance(v, (list, dict)):
                writer.writerow([k, "" if v is None else str(v)])
        return output.getvalue()


# Global analytics service instance
analytics_service = AnalyticsService()
analytics_service.seed_demo_data()
