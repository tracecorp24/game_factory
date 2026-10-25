"""Typed contracts and exceptions for Model Gateway and Budget Controller."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class ModelCapability(str, Enum):
    TEXT = "text"
    VISION = "vision"
    STRUCTURED_OUTPUT = "structured_output"
    REASONING = "reasoning"
    IMAGE_GEN = "image_generation"
    VIDEO_GEN = "video_generation"


class ModelTier(str, Enum):
    FAST_LITE = "fast_lite"
    STANDARD = "standard"
    REASONING_PRO = "reasoning_pro"


class CostKind(str, Enum):
    LLM_TOKEN = "llm_token"
    IMAGE_GENERATION = "image_generation"
    VIDEO_GENERATION = "video_generation"
    COMPUTE_SECOND = "compute_second"


class CostStatus(str, Enum):
    ESTIMATED = "estimated"
    ACTUAL = "actual"
    RECONCILED = "reconciled"
    UNPRICED = "unpriced"


class BudgetBlockedException(Exception):
    """Raised when an operation would exceed defined workspace, project, or run hard budget."""
    def __init__(self, scope: str, hard_limit: float, projected_total: float):
        super().__init__(
            f"BUDGET_BLOCKED: Exceeded {scope} hard budget limit of ${hard_limit:.4f} "
            f"(projected total: ${projected_total:.4f})"
        )
        self.scope = scope
        self.hard_limit = hard_limit
        self.projected_total = projected_total


class ModelDefinition(BaseModel):
    """Catalog specification of a supported AI model."""
    model_id: str
    provider: str
    capabilities: List[ModelCapability]
    context_window: int
    tier: ModelTier
    cost_per_million_input: float
    cost_per_million_output: float
    cost_per_million_cached: float = 0.0
    fallback_candidates: List[str] = Field(default_factory=list)
    enabled: bool = True


class TokenUsageRecord(BaseModel):
    """Standardized token accounting record conforming to shared contracts."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cached_input_tokens: Optional[int] = 0
    cache_creation_tokens: Optional[int] = 0
    reasoning_tokens: Optional[int] = 0
    billable_input_units: float = 0.0
    billable_output_units: float = 0.0
    billable_media_units: float = 0.0
    usage_source: Literal["provider_reported", "estimated", "invoice_reconciled", "missing"] = "provider_reported"


class CostEntryRecord(BaseModel):
    """Standardized financial entry recording cost of an invocation."""
    entry_id: str
    run_id: str
    project_id: Optional[str] = None
    amount: Optional[float] = None  # None if cost is unpriced/unknown
    currency: str = "USD"
    cost_kind: CostKind
    status: CostStatus
    is_unpriced: bool = False
    details: Dict[str, Any] = Field(default_factory=dict)


class BudgetLimit(BaseModel):
    """Budget constraints for a tenant workspace, project, or individual run."""
    scope_id: str
    scope_type: Literal["workspace", "project", "run"]
    soft_limit_usd: float = Field(..., ge=0.0)
    hard_limit_usd: float = Field(..., ge=0.0)
    current_spend_usd: float = Field(default=0.0, ge=0.0)

    @property
    def is_soft_limit_exceeded(self) -> bool:
        return self.current_spend_usd >= self.soft_limit_usd

    @property
    def is_hard_limit_exceeded(self) -> bool:
        return self.current_spend_usd >= self.hard_limit_usd
