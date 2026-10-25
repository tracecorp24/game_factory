"""
Experiment Metric Calculator and Statistical Significance Engine.
Provides zero-division safe formulas and two-proportion hypothesis testing.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple
from .models import ExperimentComparison, MetricValues


class MetricCalculator:
    """
    Computes performance metrics and statistical comparisons.
    Enforces the core rule:
    - Zero denominators return None (null), NEVER 0.0 and NEVER raise ZeroDivisionError.
    - Offline quality scores are NEVER conflated with real campaign metrics.
    - Premature winners are strictly forbidden before sample size and p-value gates pass.
    """

    @staticmethod
    def calculate_metrics(
        impressions: int,
        clicks: int,
        installs: int,
        spend: float,
    ) -> MetricValues:
        """Calculate CTR, IPM, and CPI with strict zero-division safety."""
        ctr: Optional[float] = None
        if impressions > 0:
            ctr = round(clicks / impressions, 6)

        ipm: Optional[float] = None
        if impressions > 0:
            ipm = round((installs / impressions) * 1000.0, 4)

        cpi: Optional[float] = None
        if installs > 0:
            cpi = round(spend / installs, 4)

        return MetricValues(
            impressions=impressions,
            clicks=clicks,
            installs=installs,
            spend=round(spend, 2),
            ctr=ctr,
            ipm=ipm,
            cpi=cpi,
        )

    @classmethod
    def compare_variants(
        cls,
        control_id: str,
        test_id: str,
        control_metrics: MetricValues,
        test_metrics: MetricValues,
        min_sample_size: int = 1000,
        significance_threshold: float = 0.05,
    ) -> ExperimentComparison:
        """
        Compare two variants using two-proportion z-test on CTR / IPM.
        Checks sample size adequacy and determines statistical significance.
        """
        n1 = control_metrics.impressions
        n2 = test_metrics.impressions
        c1 = control_metrics.clicks
        c2 = test_metrics.clicks

        total_sample = n1 + n2
        sample_reached = (n1 >= min_sample_size) and (n2 >= min_sample_size)

        delta_ctr = None
        if control_metrics.ctr is not None and test_metrics.ctr is not None:
            delta_ctr = round(test_metrics.ctr - control_metrics.ctr, 6)

        delta_ipm = None
        if control_metrics.ipm is not None and test_metrics.ipm is not None:
            delta_ipm = round(test_metrics.ipm - control_metrics.ipm, 4)

        delta_cpi = None
        if control_metrics.cpi is not None and test_metrics.cpi is not None:
            delta_cpi = round(test_metrics.cpi - control_metrics.cpi, 4)

        # Statistical test on CTR (Two-proportion Z-test)
        p_value: Optional[float] = None
        is_sig = False
        winning_id: Optional[str] = None
        rationale: str

        if n1 > 0 and n2 > 0 and (c1 + c2) > 0:
            p_value = cls._two_proportion_p_value(c1, n1, c2, n2)
            is_sig = (p_value is not None) and (p_value < significance_threshold) and sample_reached

            if not sample_reached:
                rationale = (
                    f"Sample size insufficient (Control: {n1}, Test: {n2}, Required: {min_sample_size} each). "
                    f"Winner cannot be declared prematurely."
                )
            elif is_sig:
                if delta_ctr is not None and delta_ctr > 0:
                    winning_id = test_id
                    rationale = (
                        f"Test variant won with statistically significant CTR lift of +{delta_ctr*100:.2f}% "
                        f"(p={p_value:.4f} < {significance_threshold})."
                    )
                else:
                    winning_id = control_id
                    rationale = (
                        f"Control variant maintained superiority (p={p_value:.4f} < {significance_threshold})."
                    )
            else:
                rationale = (
                    f"No statistically significant difference detected (p={p_value:.4f} >= {significance_threshold}). "
                    f"Variants perform within margin of noise."
                )
        else:
            rationale = "Zero or insufficient impressions/clicks recorded to compute statistical comparison."

        return ExperimentComparison(
            control_variant_id=control_id,
            test_variant_id=test_id,
            control_metrics=control_metrics,
            test_metrics=test_metrics,
            delta_ctr=delta_ctr,
            delta_ipm=delta_ipm,
            delta_cpi=delta_cpi,
            p_value=round(p_value, 5) if p_value is not None else None,
            is_statistically_significant=is_sig,
            sample_size_reached=sample_reached,
            winning_variant_id=winning_id,
            rationale=rationale,
        )

    @staticmethod
    def _two_proportion_p_value(count1: int, n1: int, count2: int, n2: int) -> Optional[float]:
        """Calculates two-tailed p-value for difference between two proportions."""
        if n1 == 0 or n2 == 0:
            return None

        p1 = count1 / n1
        p2 = count2 / n2
        pooled = (count1 + count2) / (n1 + n2)

        if pooled <= 0.0 or pooled >= 1.0:
            return 1.0

        se = math.sqrt(pooled * (1.0 - pooled) * (1.0 / n1 + 1.0 / n2))
        if se == 0.0:
            return 1.0

        z = abs(p1 - p2) / se

        # Two-tailed p-value from standard normal via complementary error function
        p_val = math.erfc(z / math.sqrt(2.0))
        return max(0.0, min(1.0, p_val))
