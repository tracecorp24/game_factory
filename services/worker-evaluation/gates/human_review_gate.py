"""
Gate 7: HumanReviewGate - Manages human sign-off, queue routing for ambiguous or high-risk outputs,
and immutable recording of reviewer decisions and rationales.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from services.worker_evaluation.gates.base import (
    BaseGate,
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)


class HumanReviewGate(BaseGate):
    """Gate 7: Human-in-the-Loop Approval & Review Gate."""

    gate_name: str = "human_review_gate"
    gate_version: str = "1.0.0"
    is_fatal: bool = False

    async def evaluate(self, context: GateExecutionContext) -> GateResult:
        options = context.options or {}
        human_decision = context.human_decision
        require_approval = options.get("require_human_approval", False)
        min_auto_pass_score = float(options.get("min_auto_pass_score", 3.8))
        prior_warning_present = options.get("prior_warning_present", False)

        # 1. If a human decision is already captured, evaluate it
        if human_decision:
            decision = str(human_decision.get("decision", "")).lower()
            reviewer_id = human_decision.get("reviewer_id", "system_reviewer")
            reason = human_decision.get("reason", "No reason provided")

            if decision == "approved":
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.PASSED,
                    severity=GateSeverity.INFO,
                    score=5.0,
                    message=f"Artifact officially approved by reviewer '{reviewer_id}': {reason}",
                    details={
                        "reviewer_id": reviewer_id,
                        "decision": "approved",
                        "reason": reason,
                        "reviewed_at": human_decision.get("reviewed_at"),
                    },
                )
            elif decision == "rejected":
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.ERROR,
                    score=0.0,
                    failure_code="HUMAN_REVIEW_REJECTED",
                    message=f"Artifact rejected during human QA review: {reason}",
                    details={
                        "reviewer_id": reviewer_id,
                        "decision": "rejected",
                        "reason": reason,
                        "reviewed_at": human_decision.get("reviewed_at"),
                    },
                )

        # 2. Check if human review is required
        needs_review = require_approval or prior_warning_present

        if needs_review:
            artifact_id = (context.artifact or {}).get("artifact_id", "unknown_artifact")
            run_id = (context.artifact or {}).get("run_id", "unknown_run")
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.PENDING_REVIEW,
                severity=GateSeverity.WARNING,
                score=3.0,
                failure_code="AWAITING_HUMAN_DECISION",
                message="Artifact routed to human QA review queue for final verification.",
                details={
                    "artifact_id": artifact_id,
                    "run_id": run_id,
                    "review_reasons": [
                        "Forced by policy" if require_approval else "Triggered by upstream QA warnings"
                    ],
                },
            )

        # 3. Auto-pass when no human review trigger is active
        return GateResult(
            gate_name=self.gate_name,
            gate_version=self.gate_version,
            status=GateStatus.PASSED,
            severity=GateSeverity.INFO,
            score=5.0,
            message="Automated QA gates satisfied; human review threshold bypassed by policy.",
            details={"require_approval": False},
        )
