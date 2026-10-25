"""
Decision Capture Service.
Audits user actions (select, reject, regenerate) on concept boards and emits downstream workflow events.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import ConceptBoard, ConceptDecision, DecisionAction

logger = logging.getLogger(__name__)


class DecisionCaptureError(Exception):
    """Raised when concept decision capture fails validation."""
    pass


class DecisionCaptureService:
    """
    Captures user selections, rejections, and regeneration feedback with mandatory audit reasons.
    Emits structured CONCEPT_SELECTED events to trigger downstream production workflows.
    """

    def __init__(self) -> None:
        self._decisions: List[ConceptDecision] = []
        self._concept_store: Dict[str, ConceptBoard] = {}

    def register_board(self, board: ConceptBoard) -> None:
        self._concept_store[board.concept_id] = board

    def get_board(self, concept_id: str) -> Optional[ConceptBoard]:
        return self._concept_store.get(concept_id)

    def record_decision(
        self,
        concept_id: str,
        action: DecisionAction,
        reason: str,
        actor: str = "user_operator",
        workflow_overrides: Optional[Dict[str, Any]] = None,
    ) -> ConceptDecision:
        """
        Record a decision (select, reject, regenerate) on a concept board.
        Enforces non-empty reason for audit compliance.
        """
        if not reason or not reason.strip():
            raise DecisionCaptureError(
                f"Action '{action.value}' on concept '{concept_id}' requires a mandatory explanatory reason."
            )

        board = self._concept_store.get(concept_id)
        board_id = board.board_id if board else f"unknown_board_{concept_id}"

        event_name = (
            "CONCEPT_SELECTED" if action == DecisionAction.SELECT
            else "CONCEPT_REJECTED" if action == DecisionAction.REJECT
            else "CONCEPT_REGENERATE_REQUESTED"
        )

        decision = ConceptDecision(
            decision_id=str(uuid4()),
            concept_id=concept_id,
            board_id=board_id,
            action=action,
            actor=actor,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reason=reason.strip(),
            workflow_override_params=workflow_overrides or {},
            event_type=event_name,
        )

        self._decisions.append(decision)
        logger.info(
            "Captured concept decision: action=%s, concept_id=%s, actor=%s, reason='%s'",
            action.value,
            concept_id,
            actor,
            reason,
        )
        return decision

    def list_decisions(self, concept_id: Optional[str] = None) -> List[ConceptDecision]:
        if concept_id:
            return [d for d in self._decisions if d.concept_id == concept_id]
        return list(self._decisions)

    def build_workflow_trigger_payload(self, decision: ConceptDecision) -> Dict[str, Any]:
        """Build downstream workflow trigger envelope for a selected concept."""
        if decision.action != DecisionAction.SELECT:
            raise DecisionCaptureError("Can only build workflow trigger payload for 'select' action.")

        board = self._concept_store.get(decision.concept_id)
        if not board:
            raise DecisionCaptureError(f"Concept board '{decision.concept_id}' not found in store.")

        return {
            "event_type": "CONCEPT_SELECTED",
            "concept_id": decision.concept_id,
            "board_id": decision.board_id,
            "hypothesis_id": board.hypothesis.hypothesis_id,
            "game_profile_version_id": board.hypothesis.game_profile_version_id,
            "title": board.hypothesis.title,
            "intended_hook": board.hook_frame.headline_text,
            "creative_mechanism": board.hypothesis.creative_mechanism,
            "scene_layout": board.scene_layout.model_dump(),
            "ranking_score": board.ranking.composite_score,
            "selected_at": decision.timestamp,
            "actor": decision.actor,
            "reason": decision.reason,
            "overrides": decision.workflow_override_params,
        }
