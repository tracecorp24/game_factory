"""
EvaluationService managing execution of the 7 Quality Gates, recording reviews, and storing results.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.worker_evaluation.gates.base import GateExecutionContext
from services.worker_evaluation.models import EvaluationReport, OverallVerdict
from services.worker_evaluation.pipeline import QualityGatePipeline
from services.api.app.modules.evaluations.rubrics import STANDARD_RUBRICS
from services.api.app.modules.evaluations.schemas import (
    EvaluateArtifactRequest,
    HumanReviewSubmission,
    RubricDefinitionSchema,
)

logger = logging.getLogger("api.modules.evaluations.service")


class EvaluationService:
    """Service layer for artifact evaluations, QA gates, and human reviews."""

    def __init__(self):
        self._pipeline = QualityGatePipeline()
        # In-memory store (also integrates with PostgreSQL when session is attached)
        self._evaluations: Dict[str, EvaluationReport] = {}
        self._human_reviews: Dict[str, Dict[str, Any]] = {}
        self._pending_reviews: Dict[str, Dict[str, Any]] = {}

    def get_all_rubrics(self) -> List[RubricDefinitionSchema]:
        """Return all available evaluation rubrics."""
        return list(STANDARD_RUBRICS.values())

    def get_rubric(self, rubric_id: str) -> Optional[RubricDefinitionSchema]:
        """Fetch a specific rubric by ID."""
        return STANDARD_RUBRICS.get(rubric_id)

    async def evaluate_artifact(self, req: EvaluateArtifactRequest) -> EvaluationReport:
        """Run the 7-Gate Quality Pipeline against an artifact."""
        rubric_def = self.get_rubric(req.rubric_id or "rubric_mobile_ad_v3")
        rubric_dict = rubric_def.model_dump() if rubric_def else None

        # Build execution context
        artifact_dict = {
            "artifact_id": req.artifact_id,
            "run_id": req.run_id,
            "type": req.target_type,
            "storage_ref": req.storage_ref or f"data/storage/{req.artifact_id}.{ 'png' if req.target_type == 'image' else 'mp4' if req.target_type == 'video' else 'zip' }",
            "sha256": req.media_meta.get("sha256", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
            "bytes": req.media_meta.get("bytes", 1024 * 512),
            "media_meta": req.media_meta,
        }

        # Propagate ComfyUI workflow into artifact context if present
        if "workflow_json" in req.options:
            artifact_dict["workflow_json"] = req.options["workflow_json"]
        elif "workflow_json" in req.media_meta:
            artifact_dict["workflow_json"] = req.media_meta["workflow_json"]

        context = GateExecutionContext(
            artifact=artifact_dict,
            game_dna=req.game_dna,
            creative_hypothesis=req.creative_hypothesis,
            playwright_report=req.playwright_report,
            rubric=rubric_dict,
            options=req.options,
        )

        report = await self._pipeline.run(context)

        # Store in registry
        self._evaluations[report.evaluation_id] = report

        # If needs human review, add to pending queue
        if report.overall_verdict == OverallVerdict.NEEDS_REVIEW:
            self._pending_reviews[req.artifact_id] = {
                "artifact_id": req.artifact_id,
                "evaluation_id": report.evaluation_id,
                "run_id": req.run_id,
                "queued_at": datetime.now(timezone.utc).isoformat(),
                "status": "pending",
            }
            logger.info(f"Artifact {req.artifact_id} queued for human review.")

        logger.info(
            f"Evaluated artifact {req.artifact_id}: verdict={report.overall_verdict.value}, score={report.overall_score}"
        )
        return report

    async def record_human_review(self, submission: HumanReviewSubmission) -> Dict[str, Any]:
        """Record an official human review (approval or rejection) for an artifact."""
        review_record = {
            "artifact_id": submission.artifact_id,
            "reviewer_id": submission.reviewer_id,
            "decision": submission.decision.lower(),
            "reason": submission.reason,
            "reviewed_at": datetime.now(timezone.utc).isoformat(),
            "rubric_feedback": submission.rubric_feedback or {},
        }
        self._human_reviews[submission.artifact_id] = review_record

        # Remove from pending queue if present
        self._pending_reviews.pop(submission.artifact_id, None)

        # Re-evaluate or update matching evaluation reports for this artifact
        for eval_id, report in self._evaluations.items():
            if report.artifact_id == submission.artifact_id:
                if submission.decision.lower() == "approved":
                    report.overall_verdict = OverallVerdict.PASSED
                    report.blocking_failure = None
                else:
                    report.overall_verdict = OverallVerdict.FAILED
                    report.blocking_failure = f"Human reviewer rejected: {submission.reason}"

        return review_record

    def get_evaluation(self, evaluation_id: str) -> Optional[EvaluationReport]:
        """Fetch evaluation report by ID."""
        return self._evaluations.get(evaluation_id)

    def get_evaluations_for_run(self, run_id: str) -> List[EvaluationReport]:
        """Return all evaluation reports generated during a specific run."""
        return [r for r in self._evaluations.values() if r.run_id == run_id]

    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """Return all items awaiting human review."""
        return list(self._pending_reviews.values())


# Global singleton instance
evaluation_service = EvaluationService()
