"""
ComfyUI Evaluator & Hybrid Security/QA Gateway.
Coordinates AST workflow security linting and Game DNA visual consistency gates.
CreativeForge Intelligence Studio v3.0 - Module M07 (Agent H-4).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.worker_evaluation.gates.base import (
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)
from services.worker_evaluation.gates.comfy_security_gate import ComfySecurityGate
from services.worker_evaluation.gates.comfy_visual_consistency_gate import ComfyVisualConsistencyGate
from services.worker_evaluation.security_rules import (
    SecurityIssue,
    SecurityScanReport,
    WorkflowSecurityLinter,
)

logger = logging.getLogger("api.modules.evaluations.comfy_evaluator")


class ComfyValidationRequest(BaseModel):
    """Request to validate a ComfyUI workflow JSON against AST security policies."""
    workflow_json: Dict[str, Any] = Field(description="ComfyUI graph JSON (API or UI format)")
    enforce_allowlist: bool = Field(default=True, description="Strictly enforce node allowlist")
    options: Dict[str, Any] = Field(default_factory=dict)


class ComfyValidationResponse(BaseModel):
    """Response payload of ComfyUI workflow AST security scan."""
    is_safe: bool
    scanned_nodes_count: int
    failure_code: Optional[str] = None
    summary: str
    issues: List[SecurityIssue] = Field(default_factory=list)


class ComfyHybridQAResponse(BaseModel):
    """Aggregate response combining AST Security Gate and Visual Consistency Gate."""
    is_approved: bool
    overall_score: float = Field(ge=0.0, le=5.0)
    security_verdict: GateStatus
    visual_verdict: GateStatus
    blocking_reasons: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    security_gate: GateResult
    visual_gate: GateResult


class ComfyEvaluator:
    """
    Evaluator coordinator for ComfyUI workflows and generations.
    Provides standalone linting as well as integrated hybrid quality pipeline evaluation.
    """

    def __init__(
        self,
        security_gate: Optional[ComfySecurityGate] = None,
        visual_gate: Optional[ComfyVisualConsistencyGate] = None,
    ):
        self.security_gate = security_gate or ComfySecurityGate()
        self.visual_gate = visual_gate or ComfyVisualConsistencyGate()

    def validate_workflow_ast(
        self,
        workflow_json: Dict[str, Any],
        enforce_allowlist: bool = True,
    ) -> SecurityScanReport:
        """
        Directly lints a ComfyUI workflow AST against safe node allowlists,
        path traversal patterns, and SSRF restrictions.
        """
        linter = WorkflowSecurityLinter(enforce_allowlist=enforce_allowlist)
        return linter.lint(workflow_json)

    async def evaluate_workflow_security(
        self,
        workflow_json: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
    ) -> GateResult:
        """Runs the ComfySecurityGate asynchronously against a workflow payload."""
        context = GateExecutionContext(
            artifact={"type": "comfy_workflow", "workflow_json": workflow_json},
            options=options or {},
        )
        return await self.security_gate.run(context)

    async def evaluate_image_visuals(
        self,
        artifact: Dict[str, Any],
        game_dna: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> GateResult:
        """Runs the ComfyVisualConsistencyGate against a generated image asset."""
        context = GateExecutionContext(
            artifact=artifact,
            game_dna=game_dna,
            options=options or {},
        )
        return await self.visual_gate.run(context)

    async def evaluate_hybrid_run(
        self,
        workflow_json: Optional[Dict[str, Any]] = None,
        artifact: Optional[Dict[str, Any]] = None,
        game_dna: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ComfyHybridQAResponse:
        """
        Full two-stage evaluation:
          1. AST Security Gate verifies workflow integrity.
          2. Visual Consistency Gate checks image output against Game DNA.
        """
        run_options = options or {}
        blocking_reasons: List[str] = []
        warnings: List[str] = []

        # Stage 1: Security Gate
        art = dict(artifact or {})
        if workflow_json is not None:
            art["workflow_json"] = workflow_json

        sec_context = GateExecutionContext(
            artifact=art,
            game_dna=game_dna,
            options=run_options,
        )
        sec_result = await self.security_gate.run(sec_context)

        if sec_result.status == GateStatus.FAILED:
            blocking_reasons.append(f"Security Gate failed: {sec_result.message}")

        # Stage 2: Visual Consistency Gate
        vis_context = GateExecutionContext(
            artifact=art,
            game_dna=game_dna,
            options=run_options,
        )
        vis_result = await self.visual_gate.run(vis_context)

        if vis_result.status == GateStatus.FAILED:
            blocking_reasons.append(f"Visual Consistency Gate failed: {vis_result.message}")
        elif vis_result.status == GateStatus.WARNING:
            warnings.append(f"Visual Consistency warning: {vis_result.message}")

        # Overall calculation
        is_approved = len(blocking_reasons) == 0
        if not is_approved:
            overall_score = min(sec_result.score or 0.0, vis_result.score or 0.0)
        else:
            sec_score = sec_result.score if sec_result.score is not None else 5.0
            vis_score = vis_result.score if vis_result.score is not None else 5.0
            overall_score = round(0.4 * sec_score + 0.6 * vis_score, 2)

        return ComfyHybridQAResponse(
            is_approved=is_approved,
            overall_score=overall_score,
            security_verdict=sec_result.status,
            visual_verdict=vis_result.status,
            blocking_reasons=blocking_reasons,
            warnings=warnings,
            security_gate=sec_result,
            visual_gate=vis_result,
        )


# Global singleton instance
comfy_evaluator = ComfyEvaluator()
