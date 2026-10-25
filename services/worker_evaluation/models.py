"""
Domain models for Quality Gates, Rubrics, and Evaluation Reports.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.worker_evaluation.gates.base import GateResult, GateStatus, GateSeverity


class OverallVerdict(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    WARNING = "WARNING"


class EvaluationReport(BaseModel):
    """Immutable evaluation report artifact produced by the 7-Gate QA pipeline."""
    evaluation_id: str = Field(default_factory=lambda: f"eval_{uuid.uuid4().hex[:12]}")
    run_id: str
    artifact_id: str
    target_type: str = "image"
    overall_verdict: OverallVerdict
    overall_score: float = Field(ge=0.0, le=5.0, description="Composite score on 0-5 scale")
    normalized_percent: float = Field(ge=0.0, le=100.0, description="Score on 0-100% scale")
    passed_gates_count: int = 0
    failed_gates_count: int = 0
    warning_gates_count: int = 0
    gate_results: List[GateResult] = Field(default_factory=list)
    blocking_failure: Optional[str] = None
    rubric_version: str = "rubric_v3.0_mobile_ad"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_event_payload(self) -> Dict[str, Any]:
        """Convert evaluation results to standardized EventEnvelope payload preview."""
        event_type = (
            "QUALITY_GATE_PASSED"
            if self.overall_verdict == OverallVerdict.PASSED
            else "QUALITY_GATE_FAILED"
            if self.overall_verdict == OverallVerdict.FAILED
            else "QUALITY_GATE_NEEDS_REVIEW"
        )
        return {
            "event_type": event_type,
            "evaluation_id": self.evaluation_id,
            "run_id": self.run_id,
            "artifact_id": self.artifact_id,
            "overall_verdict": self.overall_verdict.value,
            "overall_score": self.overall_score,
            "normalized_percent": self.normalized_percent,
            "blocking_failure": self.blocking_failure,
            "gate_summary": {
                res.gate_name: {"status": res.status.value, "score": res.score, "code": res.failure_code}
                for res in self.gate_results
            },
        }
