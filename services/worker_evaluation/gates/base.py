"""
Base definitions and interfaces for the 7-Layer Quality Gate pipeline.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GateStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"
    PENDING_REVIEW = "PENDING_REVIEW"


class GateSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class GateResult(BaseModel):
    """Result of a single quality gate evaluation."""
    gate_name: str
    gate_version: str = "1.0.0"
    status: GateStatus
    severity: GateSeverity = GateSeverity.INFO
    score: Optional[float] = Field(default=None, description="Score between 0.0 and 5.0 (or normalized 0-1)")
    failure_code: Optional[str] = Field(default=None, description="Actionable machine-readable code if failed")
    message: str = ""
    details: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: float = 0.0
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_blocking(self) -> bool:
        """Determines if the result should halt the pipeline immediately."""
        return self.status == GateStatus.FAILED and self.severity in (GateSeverity.ERROR, GateSeverity.FATAL)


class GateExecutionContext(BaseModel):
    """Context bundle supplied to each quality gate during evaluation."""
    artifact: Dict[str, Any] = Field(
        default_factory=dict,
        description="Artifact metadata: id, run_id, type, storage_ref, sha256, bytes, media_meta"
    )
    game_dna: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Game DNA profile and constraints: mechanics_spec, brand_constraints, do_not_generate"
    )
    creative_hypothesis: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Creative brief/hypothesis: intended_hook, emotional_arc, claims"
    )
    playwright_report: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Browser execution report: js_errors, load_time_ms, interaction_ok, screenshots"
    )
    corpus_references: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Reference assets / embeddings for similarity & IP risk scanning"
    )
    rubric: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Rubric spec for LLM Judge: criteria, weights, golden examples"
    )
    human_decision: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional pre-existing or captured human decision"
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime options: strict_mode, similarity_threshold, etc."
    )


class BaseGate(ABC):
    """Abstract base class for all quality gates."""

    gate_name: str = "base_gate"
    gate_version: str = "1.0.0"
    is_fatal: bool = False

    @abstractmethod
    async def evaluate(self, context: GateExecutionContext) -> GateResult:
        """Execute the gate evaluation and return a GateResult."""
        pass

    async def run(self, context: GateExecutionContext) -> GateResult:
        """Wrapper around evaluate measuring elapsed execution time."""
        start_time = time.perf_counter()
        try:
            result = await self.evaluate(context)
        except Exception as exc:
            result = GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL if self.is_fatal else GateSeverity.ERROR,
                failure_code=f"{self.gate_name.upper()}_EXCEPTION",
                message=f"Gate encountered unhandled exception: {str(exc)}",
                details={"exception": str(exc), "exception_type": type(exc).__name__}
            )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        result.execution_time_ms = round(elapsed_ms, 2)
        return result
