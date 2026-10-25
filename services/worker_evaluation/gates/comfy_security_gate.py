"""
ComfyUI AST Workflow Security Gate.
Statical AST linter blocking dangerous custom nodes, arbitrary code execution,
path traversal attacks, and SSRF attempts in ComfyUI workflow graphs.
CreativeForge Intelligence Studio v3.0 - Module M07 (Agent H-4).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Union

from services.worker_evaluation.gates.base import (
    BaseGate,
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)
from services.worker_evaluation.security_rules import (
    SecurityScanReport,
    WorkflowSecurityLinter,
)

logger = logging.getLogger("worker_evaluation.gates.comfy_security")


class ComfySecurityGate(BaseGate):
    """
    Gate: ComfyUI Workflow AST Security Sandbox.
    Enforces strict node allowlists, blocks arbitrary execution, path traversal, and SSRF.
    This gate is FATAL: Any security failure immediately blocks workflow execution.
    """

    gate_name: str = "comfy_security_gate"
    gate_version: str = "1.0.0"
    is_fatal: bool = True

    def __init__(self, linter: Optional[WorkflowSecurityLinter] = None):
        self.linter = linter or WorkflowSecurityLinter()

    async def evaluate(self, context: GateExecutionContext) -> GateResult:
        artifact = context.artifact or {}
        options = context.options or {}
        hypothesis = context.creative_hypothesis or {}

        # 1. Locate ComfyUI workflow JSON in execution context
        workflow_data: Optional[Union[Dict[str, Any], list]] = None

        if "workflow_json" in artifact:
            workflow_data = artifact["workflow_json"]
        elif "raw_workflow" in artifact:
            workflow_data = artifact["raw_workflow"]
        elif "workflow_json" in options:
            workflow_data = options["workflow_json"]
        elif "workflow_json" in hypothesis:
            workflow_data = hypothesis["workflow_json"]
        elif "workflow" in artifact:
            workflow_data = artifact["workflow"]

        artifact_type = str(artifact.get("type", "")).lower()

        # 2. Check if workflow is missing when required
        if workflow_data is None:
            if artifact_type in ("comfy_workflow", "comfy_preset", "workflow_json") or options.get("strict_workflow_required", False):
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.FATAL,
                    score=0.0,
                    failure_code="WORKFLOW_SECURITY_VIOLATION",
                    message="Missing ComfyUI workflow payload in artifact context for security verification.",
                    details={"artifact_type": artifact_type},
                )
            # Standalone visual asset without embedded workflow can skip AST graph linting
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.SKIPPED,
                severity=GateSeverity.INFO,
                score=5.0,
                message=f"No ComfyUI workflow graph found in artifact '{artifact.get('artifact_id', 'unknown')}'; AST linting skipped.",
                details={"artifact_type": artifact_type},
            )

        # 3. Configure linter with any contextual allowed domains
        custom_domains = set(options.get("allowed_domains", []))
        game_dna = context.game_dna or {}
        asset_rights = game_dna.get("asset_rights", {})
        if isinstance(asset_rights, dict) and "allowed_domains" in asset_rights:
            custom_domains.update(asset_rights["allowed_domains"])

        linter = self.linter
        if custom_domains:
            linter = WorkflowSecurityLinter(
                node_allowlist=self.linter.node_allowlist,
                node_blocklist=self.linter.node_blocklist,
                allowed_domains=custom_domains,
                enforce_allowlist=self.linter.enforce_allowlist,
            )

        # Execute AST Security Scan
        report: SecurityScanReport = linter.lint(workflow_data)

        if not report.is_safe:
            # Build clear, actionable violation summary
            issue_descriptions = [f"[{issue.issue_type.value}] {issue.message}" for issue in report.issues]
            logger.warning(
                f"ComfySecurityGate rejected workflow: {len(report.issues)} issue(s) detected. First issue: {issue_descriptions[0] if issue_descriptions else ''}"
            )

            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL,
                score=0.0,
                failure_code="WORKFLOW_SECURITY_VIOLATION",
                message=f"ComfyUI workflow security scan failed: {report.summary}",
                details={
                    "scanned_nodes_count": report.scanned_nodes_count,
                    "issues_count": len(report.issues),
                    "issues": [issue.model_dump() for issue in report.issues],
                    "failure_code": report.failure_code or "WORKFLOW_SECURITY_VIOLATION",
                },
            )

        # 4. Safe workflow passed AST security linting
        logger.info(
            f"ComfySecurityGate passed: {report.scanned_nodes_count} nodes checked successfully."
        )

        return GateResult(
            gate_name=self.gate_name,
            gate_version=self.gate_version,
            status=GateStatus.PASSED,
            severity=GateSeverity.INFO,
            score=5.0,
            message=f"ComfyUI workflow passed AST security linting ({report.scanned_nodes_count} nodes verified).",
            details={
                "scanned_nodes_count": report.scanned_nodes_count,
                "is_safe": True,
            },
        )
