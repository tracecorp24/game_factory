"""
Gate 2: TechnicalGate - Validates technical integrity, file limits, and Playwright browser QA reports (zero JS error rule).
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from services.worker_evaluation.gates.base import (
    BaseGate,
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)

# Maximum allowed artifact size limits in bytes
MAX_SIZE_LIMITS: Dict[str, int] = {
    "image": 30 * 1024 * 1024,        # 30 MB
    "video": 150 * 1024 * 1024,      # 150 MB
    "playable_zip": 50 * 1024 * 1024, # 50 MB
    "concept_board": 25 * 1024 * 1024,# 25 MB
    "manifest": 5 * 1024 * 1024,      # 5 MB
    "evaluation_report": 5 * 1024 * 1024, # 5 MB
}

VALID_EXTENSIONS: Dict[str, List[str]] = {
    "image": [".png", ".jpg", ".jpeg", ".webp"],
    "video": [".mp4", ".webm", ".mov"],
    "playable_zip": [".zip", ".html"],
    "concept_board": [".json", ".png", ".jpg"],
    "manifest": [".json"],
    "evaluation_report": [".json"],
}


class TechnicalGate(BaseGate):
    """Gate 2: Technical Integrity and Browser QA Gate."""

    gate_name: str = "technical_gate"
    gate_version: str = "1.0.0"
    is_fatal: bool = True  # Technical failures are fatal and must stop pipeline

    async def evaluate(self, context: GateExecutionContext) -> GateResult:
        artifact = context.artifact
        artifact_type = str(artifact.get("type", "")).lower()
        storage_ref = artifact.get("storage_ref", "")
        byte_size = artifact.get("bytes", 0)

        # 1. Size bounds check
        max_allowed = MAX_SIZE_LIMITS.get(artifact_type, 100 * 1024 * 1024)
        if byte_size > max_allowed:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL,
                score=0.0,
                failure_code="TECHNICAL_SIZE_LIMIT_EXCEEDED",
                message=f"Artifact size ({byte_size} bytes) exceeds limit of {max_allowed} bytes for type '{artifact_type}'.",
                details={"bytes": byte_size, "max_allowed": max_allowed, "type": artifact_type},
            )

        # 2. File extension & format integrity check
        if storage_ref:
            _, ext = os.path.splitext(storage_ref)
            ext_clean = ext.lower().split("?")[0]  # remove query params if url
            allowed_exts = VALID_EXTENSIONS.get(artifact_type, [])
            if allowed_exts and ext_clean and ext_clean not in allowed_exts:
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.FATAL,
                    score=0.0,
                    failure_code="TECHNICAL_INVALID_FORMAT_EXTENSION",
                    message=f"Storage extension '{ext_clean}' is not supported for artifact type '{artifact_type}'. Allowed: {allowed_exts}",
                    details={"storage_ref": storage_ref, "extension": ext_clean, "allowed": allowed_exts},
                )

        # 3. Playwright browser test verification (Zero JS errors rule)
        playwright_report = context.playwright_report
        # If artifact is playable or a playwright report is provided, strictly enforce QA checks
        if artifact_type == "playable_zip" or playwright_report is not None:
            if not playwright_report:
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.FATAL,
                    score=0.0,
                    failure_code="PLAYWRIGHT_REPORT_MISSING",
                    message="Playable artifact requires a completed Playwright Browser QA report.",
                    details={"artifact_type": artifact_type},
                )

            # Check for runtime JS errors in browser console
            js_errors = playwright_report.get("js_errors", [])
            if js_errors:
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.FATAL,
                    score=0.0,
                    failure_code="PLAYWRIGHT_JS_ERROR",
                    message=f"Playwright detected {len(js_errors)} runtime JavaScript errors during execution. Zero JS error policy violated.",
                    details={
                        "js_errors": js_errors[:5],
                        "total_js_errors": len(js_errors),
                        "viewport": playwright_report.get("viewport"),
                    },
                )

            # Check for HTTP 4xx/5xx network failures during loading assets
            http_errors = playwright_report.get("http_errors", [])
            if http_errors:
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.FATAL,
                    score=0.0,
                    failure_code="PLAYWRIGHT_ASSET_LOAD_FAILED",
                    message=f"Playwright detected {len(http_errors)} asset HTTP request errors (4xx/5xx).",
                    details={"http_errors": http_errors[:5], "total_http_errors": len(http_errors)},
                )

            # Check interaction result
            interaction_passed = playwright_report.get("interaction_passed", True)
            if not interaction_passed:
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.FATAL,
                    score=1.0,
                    failure_code="PLAYWRIGHT_INTERACTION_FAILED",
                    message="Simulated user swipe/touch interaction failed during playable QA test.",
                    details={
                        "interaction_log": playwright_report.get("interaction_log", []),
                        "failure_step": playwright_report.get("failure_step"),
                    },
                )

            # Check load time
            load_time_ms = playwright_report.get("page_load_ms", 0)
            if load_time_ms > 8000:
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.ERROR,
                    score=2.0,
                    failure_code="PLAYWRIGHT_LOAD_TIMEOUT",
                    message=f"Page load time ({load_time_ms} ms) exceeded maximum latency threshold (8000 ms).",
                    details={"page_load_ms": load_time_ms, "threshold_ms": 8000},
                )

        return GateResult(
            gate_name=self.gate_name,
            gate_version=self.gate_version,
            status=GateStatus.PASSED,
            severity=GateSeverity.INFO,
            score=5.0,
            message="Technical gate passed: file size limits respected, zero JS errors, format verified.",
            details={
                "byte_size": byte_size,
                "storage_ref": storage_ref,
                "playwright_verified": bool(playwright_report),
            },
        )
