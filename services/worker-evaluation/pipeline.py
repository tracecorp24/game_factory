"""
7-Layer Quality Gate Pipeline Orchestrator.
Executes Schema, Technical, GameTruth, Visual, Similarity, LLMJudge, and HumanReview gates sequentially.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

import logging
from typing import List, Optional
from services.worker_evaluation.gates.base import (
    BaseGate,
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)
from services.worker_evaluation.gates.schema_gate import SchemaGate
from services.worker_evaluation.gates.technical_gate import TechnicalGate
from services.worker_evaluation.gates.game_truth_gate import GameTruthGate
from services.worker_evaluation.gates.visual_gate import VisualGate
from services.worker_evaluation.gates.similarity_gate import SimilarityGate
from services.worker_evaluation.gates.llm_judge_gate import LLMJudgeGate
from services.worker_evaluation.gates.human_review_gate import HumanReviewGate
from services.worker_evaluation.gates.comfy_security_gate import ComfySecurityGate
from services.worker_evaluation.gates.comfy_visual_consistency_gate import ComfyVisualConsistencyGate
from services.worker_evaluation.models import EvaluationReport, OverallVerdict

logger = logging.getLogger("worker_evaluation.pipeline")


class QualityGatePipeline:
    """
    Sequential Quality Gate Pipeline runner.
    Supports standard 7-Layer QA as well as ComfyUI Deep Hybrid architecture.
    """

    def __init__(
        self,
        custom_gates: Optional[List[BaseGate]] = None,
        enable_comfy_gates: bool = False,
    ):
        if custom_gates is not None:
            self.gates = list(custom_gates)
        else:
            base_gates = [
                SchemaGate(),
                TechnicalGate(),
                GameTruthGate(),
                VisualGate(),
                SimilarityGate(),
                LLMJudgeGate(),
                HumanReviewGate(),
            ]
            if enable_comfy_gates:
                self.gates = [
                    ComfySecurityGate(),
                    SchemaGate(),
                    TechnicalGate(),
                    GameTruthGate(),
                    VisualGate(),
                    ComfyVisualConsistencyGate(),
                    SimilarityGate(),
                    LLMJudgeGate(),
                    HumanReviewGate(),
                ]
            else:
                self.gates = base_gates

    @classmethod
    def for_comfy(cls) -> "QualityGatePipeline":
        """Factory for a hybrid quality pipeline including ComfyUI AST Security & Visual QA gates."""
        return cls(enable_comfy_gates=True)

    async def run(self, context: GateExecutionContext) -> EvaluationReport:
        """Run all gates in order, propagating warnings and halting on fatal failures."""
        gate_results: List[GateResult] = []
        blocking_failure: Optional[str] = None
        has_warnings = False
        has_fatal_failure = False

        run_id = (context.artifact or {}).get("run_id", "unassigned_run")
        artifact_id = (context.artifact or {}).get("artifact_id", "unassigned_artifact")
        artifact_type = str((context.artifact or {}).get("type", "unknown")).lower()

        # Dynamic contextual hybrid activation: auto-protect ComfyUI workflows
        active_gates = list(self.gates)
        is_comfy_workflow = (
            artifact_type in ("comfy_workflow", "comfy_preset")
            or "workflow_json" in (context.artifact or {})
            or context.options.get("enable_comfy_gates", False)
        )
        gate_names = {g.gate_name for g in active_gates}
        if is_comfy_workflow and "comfy_security_gate" not in gate_names:
            active_gates.insert(0, ComfySecurityGate())
            if artifact_type == "image" and "comfy_visual_consistency_gate" not in gate_names:
                active_gates.append(ComfyVisualConsistencyGate())

        for gate in active_gates:
            # Propagate contextual warnings to downstream gates (e.g. human review)
            if has_warnings:
                context.options["prior_warning_present"] = True

            res = await gate.run(context)
            gate_results.append(res)

            if res.status == GateStatus.WARNING:
                has_warnings = True

            # If gate failed with fatal/blocking severity, halt subsequent gates
            if res.is_blocking:
                has_fatal_failure = True
                blocking_failure = f"{res.gate_name}: {res.failure_code or res.message}"
                logger.warning(
                    f"Pipeline halted by blocking gate failure: {blocking_failure} on artifact {artifact_id}"
                )
                break

        # Compute summary metrics
        passed_count = sum(1 for r in gate_results if r.status == GateStatus.PASSED)
        failed_count = sum(1 for r in gate_results if r.status == GateStatus.FAILED)
        warning_count = sum(1 for r in gate_results if r.status == GateStatus.WARNING)
        pending_review_count = sum(1 for r in gate_results if r.status == GateStatus.PENDING_REVIEW)

        # Calculate composite score from scored gates
        scores = [r.score for r in gate_results if r.score is not None]
        overall_score = round(sum(scores) / len(scores), 2) if scores else 0.0
        normalized_percent = round((overall_score / 5.0) * 100.0, 1)

        # Determine overall verdict
        if has_fatal_failure or failed_count > 0:
            verdict = OverallVerdict.FAILED
        elif pending_review_count > 0:
            verdict = OverallVerdict.NEEDS_REVIEW
        elif warning_count > 0:
            verdict = OverallVerdict.WARNING
        else:
            verdict = OverallVerdict.PASSED

        rubric_version = (context.rubric or {}).get("version", "rubric_v3.0_mobile_ad")

        report = EvaluationReport(
            run_id=run_id,
            artifact_id=artifact_id,
            target_type=artifact_type,
            overall_verdict=verdict,
            overall_score=overall_score,
            normalized_percent=normalized_percent,
            passed_gates_count=passed_count,
            failed_gates_count=failed_count,
            warning_gates_count=warning_count,
            gate_results=gate_results,
            blocking_failure=blocking_failure,
            rubric_version=rubric_version,
        )

        return report
