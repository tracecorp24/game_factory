"""
Gate 4: VisualGate - Validates visual standards, resolution, aspect ratio (9:16), contrast, and CTA readability.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional
from services.worker_evaluation.gates.base import (
    BaseGate,
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)

# Standard video/image aspect ratio targets (width / height)
TARGET_ASPECT_RATIOS = {
    "9:16": 9.0 / 16.0,   # 0.5625 (Standard Mobile Vertical Ad)
    "1:1": 1.0,           # Square Feed Ad
    "4:5": 4.0 / 5.0,     # 0.80 Instagram / TikTok Feed
    "16:9": 16.0 / 9.0,   # 1.7778 Landscape
}

DEFAULT_TARGET = "9:16"
TOLERANCE = 0.03  # 3% tolerance


class VisualGate(BaseGate):
    """Gate 4: Visual Quality, Aspect Ratio & CTA Readability Gate."""

    gate_name: str = "visual_gate"
    gate_version: str = "1.0.0"
    is_fatal: bool = False

    async def evaluate(self, context: GateExecutionContext) -> GateResult:
        artifact = context.artifact or {}
        artifact_type = str(artifact.get("type", "")).lower()
        media_meta = artifact.get("media_meta", {})
        options = context.options or {}

        # Non-visual artifacts (like manifest or report) can skip visual inspection
        if artifact_type in ("manifest", "evaluation_report"):
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.SKIPPED,
                severity=GateSeverity.INFO,
                score=5.0,
                message=f"Visual gate skipped for non-visual artifact type '{artifact_type}'.",
            )

        width = media_meta.get("width")
        height = media_meta.get("height")

        # 1. Check dimensions
        if width is None or height is None or width <= 0 or height <= 0:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.ERROR,
                score=1.0,
                failure_code="VISUAL_MISSING_DIMENSIONS",
                message=f"Missing or invalid dimensions in media_meta: width={width}, height={height}",
                details={"media_meta": media_meta},
            )

        # 2. Check Aspect Ratio (Default target: 9:16 vertical)
        expected_ratio_name = options.get("target_aspect_ratio", DEFAULT_TARGET)
        target_ratio = TARGET_ASPECT_RATIOS.get(expected_ratio_name, TARGET_ASPECT_RATIOS[DEFAULT_TARGET])
        actual_ratio = float(width) / float(height)

        if abs(actual_ratio - target_ratio) > TOLERANCE:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.ERROR,
                score=2.0,
                failure_code="VISUAL_INVALID_ASPECT_RATIO",
                message=f"Aspect ratio {width}x{height} ({actual_ratio:.4f}) deviates from expected {expected_ratio_name} ({target_ratio:.4f}).",
                details={
                    "actual_ratio": round(actual_ratio, 4),
                    "expected_ratio": round(target_ratio, 4),
                    "expected_preset": expected_ratio_name,
                    "width": width,
                    "height": height,
                },
            )

        # 3. Check Minimum Resolution (Min 720p)
        min_width = options.get("min_width", 720)
        min_height = options.get("min_height", 1280)
        if width < min_width or height < min_height:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.ERROR,
                score=2.5,
                failure_code="VISUAL_LOW_RESOLUTION",
                message=f"Artifact resolution {width}x{height} is below minimum required {min_width}x{min_height}.",
                details={"width": width, "height": height, "min_width": min_width, "min_height": min_height},
            )

        # 4. CTA and Contrast Evaluation
        score = 5.0
        warnings: List[str] = []

        # If CTA metadata is present, evaluate contrast & sizing
        cta_text = media_meta.get("cta_text")
        contrast_ratio = media_meta.get("contrast_ratio")  # e.g., 4.8
        if cta_text is not None:
            if not cta_text or len(str(cta_text).strip()) == 0:
                warnings.append("CTA text is empty.")
                score -= 1.0

        if contrast_ratio is not None:
            # WCAG AA standard for large text is 3.0:1, normal text is 4.5:1
            if contrast_ratio < 3.0:
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.ERROR,
                    score=2.0,
                    failure_code="VISUAL_LOW_CTA_CONTRAST",
                    message=f"CTA text contrast ratio ({contrast_ratio:.2f}:1) fails WCAG minimum threshold (3.0:1).",
                    details={"contrast_ratio": contrast_ratio, "threshold": 3.0},
                )
            elif contrast_ratio < 4.5:
                warnings.append(f"CTA contrast ratio {contrast_ratio:.2f}:1 is acceptable but below recommended 4.5:1.")
                score -= 0.5

        # 5. Video specific checks (duration and fps)
        if artifact_type == "video":
            duration_sec = media_meta.get("duration_sec", 0)
            if duration_sec < 3.0 or duration_sec > 65.0:
                return GateResult(
                    gate_name=self.gate_name,
                    gate_version=self.gate_version,
                    status=GateStatus.FAILED,
                    severity=GateSeverity.ERROR,
                    score=2.0,
                    failure_code="VISUAL_INVALID_VIDEO_DURATION",
                    message=f"Video duration {duration_sec}s outside acceptable ad creative bounds (3s - 65s).",
                    details={"duration_sec": duration_sec},
                )
            fps = media_meta.get("fps")
            if fps is not None and fps < 24:
                warnings.append(f"Video framerate {fps} fps is below smooth playback target of 24 fps.")
                score -= 0.5

        return GateResult(
            gate_name=self.gate_name,
            gate_version=self.gate_version,
            status=GateStatus.PASSED,
            severity=GateSeverity.INFO,
            score=round(score, 2),
            message=f"Visual quality standards passed for {expected_ratio_name} ({width}x{height}).",
            details={
                "aspect_ratio": f"{width}x{height}",
                "resolution_tier": "HD" if width >= 1080 else "Standard",
                "warnings": warnings,
            },
        )
