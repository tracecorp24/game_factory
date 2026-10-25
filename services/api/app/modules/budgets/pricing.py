"""Price catalog and token/media cost calculation engine."""

from __future__ import annotations

from typing import Dict, Optional, Tuple
from .types import CostKind, CostStatus, ModelDefinition, ModelTier, ModelCapability


class PriceCatalog:
    """
    Catalog of AI model and media rendering pricing rates.
    Enforces strict non-double-counting of cached input tokens and
    explicit unpriced status for unknown external media calls.
    """

    # Pre-configured pricing rates per 1 Million tokens (USD)
    MODELS: Dict[str, ModelDefinition] = {
        "gpt-4o": ModelDefinition(
            model_id="gpt-4o",
            provider="openai",
            capabilities=[ModelCapability.TEXT, ModelCapability.VISION, ModelCapability.STRUCTURED_OUTPUT],
            context_window=128000,
            tier=ModelTier.STANDARD,
            cost_per_million_input=2.50,
            cost_per_million_output=10.00,
            cost_per_million_cached=1.25,
            fallback_candidates=["claude-3-5-sonnet", "gpt-4o-mini"],
        ),
        "gpt-4o-mini": ModelDefinition(
            model_id="gpt-4o-mini",
            provider="openai",
            capabilities=[ModelCapability.TEXT, ModelCapability.VISION, ModelCapability.STRUCTURED_OUTPUT],
            context_window=128000,
            tier=ModelTier.FAST_LITE,
            cost_per_million_input=0.15,
            cost_per_million_output=0.60,
            cost_per_million_cached=0.075,
            fallback_candidates=["gemini-1.5-flash"],
        ),
        "claude-3-5-sonnet": ModelDefinition(
            model_id="claude-3-5-sonnet",
            provider="anthropic",
            capabilities=[ModelCapability.TEXT, ModelCapability.VISION, ModelCapability.STRUCTURED_OUTPUT],
            context_window=200000,
            tier=ModelTier.STANDARD,
            cost_per_million_input=3.00,
            cost_per_million_output=15.00,
            cost_per_million_cached=0.30,
            fallback_candidates=["gpt-4o"],
        ),
        "gemini-1.5-pro": ModelDefinition(
            model_id="gemini-1.5-pro",
            provider="google",
            capabilities=[ModelCapability.TEXT, ModelCapability.VISION, ModelCapability.STRUCTURED_OUTPUT, ModelCapability.REASONING],
            context_window=1000000,
            tier=ModelTier.STANDARD,
            cost_per_million_input=1.25,
            cost_per_million_output=5.00,
            cost_per_million_cached=0.3125,
            fallback_candidates=["gpt-4o"],
        ),
        "gemini-1.5-flash": ModelDefinition(
            model_id="gemini-1.5-flash",
            provider="google",
            capabilities=[ModelCapability.TEXT, ModelCapability.VISION, ModelCapability.STRUCTURED_OUTPUT],
            context_window=1000000,
            tier=ModelTier.FAST_LITE,
            cost_per_million_input=0.075,
            cost_per_million_output=0.30,
            cost_per_million_cached=0.01875,
            fallback_candidates=["gpt-4o-mini"],
        ),
        "o1": ModelDefinition(
            model_id="o1",
            provider="openai",
            capabilities=[ModelCapability.TEXT, ModelCapability.REASONING, ModelCapability.STRUCTURED_OUTPUT],
            context_window=200000,
            tier=ModelTier.REASONING_PRO,
            cost_per_million_input=15.00,
            cost_per_million_output=60.00,
            cost_per_million_cached=7.50,
            fallback_candidates=["gemini-1.5-pro"],
        ),
        "mock-fast-model": ModelDefinition(
            model_id="mock-fast-model",
            provider="mock",
            capabilities=[ModelCapability.TEXT, ModelCapability.STRUCTURED_OUTPUT],
            context_window=32000,
            tier=ModelTier.FAST_LITE,
            cost_per_million_input=0.10,
            cost_per_million_output=0.20,
            cost_per_million_cached=0.05,
            fallback_candidates=[],
        ),
    }

    # Known fixed rates for media calls
    KNOWN_MEDIA_RATES: Dict[str, float] = {
        "dall-e-3-hd": 0.080,
        "dall-e-3-standard": 0.040,
        "remotion_compute_per_second": 0.005,
    }

    @classmethod
    def get_model(cls, model_id: str) -> Optional[ModelDefinition]:
        return cls.MODELS.get(model_id)

    @classmethod
    def register_model(cls, model_def: ModelDefinition) -> None:
        cls.MODELS[model_def.model_id] = model_def

    @classmethod
    def calculate_token_cost(
        cls,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        reasoning_tokens: int = 0,
        provider_total_includes_cached: bool = True,
    ) -> Tuple[float, float, float, float]:
        """
        Calculates exact dollar cost for token usage without double counting.
        
        Formula:
        If provider reported total input tokens already includes cached tokens,
        then net non-cached input = max(0, input_tokens - cached_tokens).
        
        Returns:
            (total_cost, uncached_input_cost, cached_input_cost, output_cost)
        """
        model = cls.get_model(model_id)
        if not model:
            # Default fallback conservative baseline rates if model not in catalog
            rate_in = 2.0
            rate_out = 8.0
            rate_cached = 0.5
        else:
            rate_in = model.cost_per_million_input
            rate_out = model.cost_per_million_output
            rate_cached = model.cost_per_million_cached

        # Strict double-counting prevention
        if provider_total_includes_cached and cached_tokens > 0:
            billable_uncached_input = max(0, input_tokens - cached_tokens)
        else:
            billable_uncached_input = input_tokens

        uncached_cost = (billable_uncached_input / 1_000_000.0) * rate_in
        cached_cost = (cached_tokens / 1_000_000.0) * rate_cached
        output_cost = (output_tokens / 1_000_000.0) * rate_out

        total_cost = uncached_cost + cached_cost + output_cost
        return round(total_cost, 6), round(uncached_cost, 6), round(cached_cost, 6), round(output_cost, 6)

    @classmethod
    def calculate_media_cost(
        cls,
        provider_key: str,
        units: float = 1.0,
    ) -> Tuple[Optional[float], bool, CostStatus]:
        """
        Calculates media cost. If provider or rate is unknown, returns:
        (None, True, CostStatus.UNPRICED).
        Never defaults unknown costs to 0!
        """
        if provider_key in cls.KNOWN_MEDIA_RATES:
            unit_rate = cls.KNOWN_MEDIA_RATES[provider_key]
            amount = round(unit_rate * units, 6)
            return amount, False, CostStatus.ACTUAL

        # Unknown media provider: must be explicitly marked unpriced
        return None, True, CostStatus.UNPRICED
