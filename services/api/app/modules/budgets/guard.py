"""M09 - Hierarchical Budget Guard and Threshold Controller."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from .types import BudgetBlockedException, BudgetLimit

logger = logging.getLogger("budgets.guard")


class BudgetGuard:
    """
    Guards workspace, project, and run financial boundaries.
    Performs pre-flight checks against hard limits and issues soft limit alerts.
    """

    def __init__(self) -> None:
        # Key: (scope_type, scope_id) -> BudgetLimit
        self._limits: Dict[str, BudgetLimit] = {}

    def set_budget(
        self,
        scope_id: str,
        scope_type: str,
        soft_limit_usd: float,
        hard_limit_usd: float,
        current_spend_usd: float = 0.0,
    ) -> BudgetLimit:
        """Configures or updates budget constraints for a scope."""
        if soft_limit_usd > hard_limit_usd:
            raise ValueError(f"Soft limit (${soft_limit_usd}) cannot exceed hard limit (${hard_limit_usd})")

        key = f"{scope_type}:{scope_id}"
        limit = BudgetLimit(
            scope_id=scope_id,
            scope_type=scope_type,  # type: ignore
            soft_limit_usd=soft_limit_usd,
            hard_limit_usd=hard_limit_usd,
            current_spend_usd=current_spend_usd,
        )
        self._limits[key] = limit
        return limit

    def get_budget(self, scope_id: str, scope_type: str) -> Optional[BudgetLimit]:
        key = f"{scope_type}:{scope_id}"
        return self._limits.get(key)

    def check_budget_before_call(
        self,
        estimated_cost_usd: float,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Pre-flight check before dispatching an LLM or media generation call.
        
        If projected spend exceeds any hard limit, raises BudgetBlockedException immediately.
        Returns a list of soft limit warning events if any soft limit is crossed.
        """
        warnings: List[Dict[str, Any]] = []

        scopes = [
            ("workspace", workspace_id),
            ("project", project_id),
            ("run", run_id),
        ]

        for scope_type, scope_id in scopes:
            if not scope_id:
                continue

            limit = self.get_budget(scope_id, scope_type)
            if not limit:
                continue

            projected_total = limit.current_spend_usd + estimated_cost_usd

            # 1. Hard deny check
            if projected_total > limit.hard_limit_usd:
                logger.error(
                    "Budget hard limit exceeded on %s '%s': limit=$%.4f, current=$%.4f, est=$%.4f",
                    scope_type, scope_id, limit.hard_limit_usd, limit.current_spend_usd, estimated_cost_usd
                )
                raise BudgetBlockedException(
                    scope=f"{scope_type} ({scope_id})",
                    hard_limit=limit.hard_limit_usd,
                    projected_total=projected_total,
                )

            # 2. Soft alert check
            if projected_total >= limit.soft_limit_usd:
                warnings.append({
                    "event_type": "BUDGET_SOFT_LIMIT_EXCEEDED",
                    "scope_type": scope_type,
                    "scope_id": scope_id,
                    "soft_limit_usd": limit.soft_limit_usd,
                    "projected_total_usd": round(projected_total, 4),
                    "hard_limit_usd": limit.hard_limit_usd,
                })

        return warnings

    def record_spend(
        self,
        actual_cost_usd: float,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> None:
        """Atomically increments cumulative spend across all active scopes."""
        scopes = [
            ("workspace", workspace_id),
            ("project", project_id),
            ("run", run_id),
        ]

        for scope_type, scope_id in scopes:
            if not scope_id:
                continue
            limit = self.get_budget(scope_id, scope_type)
            if limit:
                limit.current_spend_usd = round(limit.current_spend_usd + actual_cost_usd, 6)
