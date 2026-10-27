"""
Concept Intelligence Application Service.
Provides end-to-end orchestration for concept ideation, heuristic ranking, and user decision capture.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import (
    ConceptBoard,
    ConceptDecision,
    CreativeHypothesis,
    DecisionAction,
    RankingEvaluation,
    RankingWeights,
)
from .ideation import IdeationAgent
from .ranking import ConceptRankingEngine
from .board_generator import ConceptBoardGenerator
from .decision_capture import DecisionCaptureService
import sys
import os
import importlib.util

if "services.worker_trends" not in sys.modules:
    wt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../worker-trends"))
    if wt_dir not in sys.path:
        sys.path.insert(0, wt_dir)
    spec = importlib.util.spec_from_file_location("worker_trends", os.path.join(wt_dir, "__init__.py"))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules["worker_trends"] = mod
        sys.modules["services.worker_trends"] = mod
        spec.loader.exec_module(mod)

from services.api.app.modules.game_dna.models import GameProfileVersion
from services.worker_trends.models import TrendReport


class ConceptService:
    """
    Coordinates hypothesis generation, 6-dimension heuristic ranking,
    concept board rendering, and user audit decisions.
    """

    def __init__(
        self,
        ideation_agent: Optional[IdeationAgent] = None,
        ranking_engine: Optional[ConceptRankingEngine] = None,
        board_generator: Optional[ConceptBoardGenerator] = None,
        decision_service: Optional[DecisionCaptureService] = None,
    ):
        self.ideation = ideation_agent or IdeationAgent()
        self.ranking = ranking_engine or ConceptRankingEngine()
        self.board_gen = board_generator or ConceptBoardGenerator()
        self.decisions = decision_service or DecisionCaptureService()
        self._hypotheses: Dict[str, CreativeHypothesis] = {}

    def generate_and_rank_concepts(
        self,
        trend_report: TrendReport,
        profile_version: GameProfileVersion,
        count: int = 4,
        weights_override: Optional[RankingWeights] = None,
        target_audience: Optional[str] = None,
    ) -> List[ConceptBoard]:
        """
        Generates 3 to 8 hypotheses, evaluates each via the heuristic formula,
        and constructs interactive ConceptBoards.
        """
        hypotheses = self.ideation.generate_hypotheses(
            trend_report=trend_report,
            profile_version=profile_version,
            count=count,
            target_audience=target_audience,
        )

        boards: List[ConceptBoard] = []
        for hypo in hypotheses:
            self._hypotheses[hypo.hypothesis_id] = hypo
            ranking_eval = self.ranking.evaluate_hypothesis(
                hypothesis=hypo,
                profile_version=profile_version,
                weights_override=weights_override,
            )
            board = self.board_gen.generate_board(
                hypothesis=hypo,
                ranking=ranking_eval,
                profile_version=profile_version,
            )
            self.decisions.register_board(board)
            boards.append(board)

    async def generate_and_rank_concepts_async(
        self,
        trend_report: TrendReport,
        profile_version: GameProfileVersion,
        count: int = 4,
        weights_override: Optional[RankingWeights] = None,
        target_audience: Optional[str] = None,
    ) -> List[ConceptBoard]:
        """
        Asynchronously generates 3 to 8 hypotheses (leveraging live LLMs if configured),
        evaluates each via the heuristic formula, and constructs interactive ConceptBoards.
        """
        hypotheses = await self.ideation.generate_hypotheses_async(
            trend_report=trend_report,
            profile_version=profile_version,
            count=count,
            target_audience=target_audience,
        )

        boards: List[ConceptBoard] = []
        for hypo in hypotheses:
            self._hypotheses[hypo.hypothesis_id] = hypo
            ranking_eval = self.ranking.evaluate_hypothesis(
                hypothesis=hypo,
                profile_version=profile_version,
                weights_override=weights_override,
            )
            board = self.board_gen.generate_board(
                hypothesis=hypo,
                ranking=ranking_eval,
                profile_version=profile_version,
            )
            self.decisions.register_board(board)
            boards.append(board)

        # Sort boards by composite ranking score descending
        boards.sort(key=lambda b: b.ranking.composite_score, reverse=True)
        return boards

    def get_board(self, concept_id: str) -> Optional[ConceptBoard]:
        return self.decisions.get_board(concept_id)

    def record_user_decision(
        self,
        concept_id: str,
        action: DecisionAction,
        reason: str,
        actor: str = "user_operator",
        workflow_overrides: Optional[Dict[str, Any]] = None,
    ) -> ConceptDecision:
        """Capture user choice with required audit reasoning."""
        return self.decisions.record_decision(
            concept_id=concept_id,
            action=action,
            reason=reason,
            actor=actor,
            workflow_overrides=workflow_overrides,
        )

    def build_workflow_envelope(self, decision: ConceptDecision) -> Dict[str, Any]:
        """Generate downstream payload when concept is selected."""
        return self.decisions.build_workflow_trigger_payload(decision)
