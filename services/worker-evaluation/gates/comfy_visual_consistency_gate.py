"""
Gate: ComfyVisualConsistencyGate - Evaluates ComfyUI image generations against Game DNA.
Checks color palette fidelity, edge sharpness (Laplacian variance), exposure/contrast anomalies,
and style token consistency (0.00 - 1.00 score).
CreativeForge Intelligence Studio v3.0 - Module M07 (Agent H-4).
"""

from __future__ import annotations

import base64
import io
import logging
import math
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from PIL import Image, ImageFilter, ImageStat
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from services.worker_evaluation.gates.base import (
    BaseGate,
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)

logger = logging.getLogger("worker_evaluation.gates.comfy_visual_consistency")


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    """Convert hex color code string (#RRGGBB or #RGB) to (r, g, b) tuple."""
    hex_clean = hex_code.strip().lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)
    if len(hex_clean) != 6:
        return (128, 128, 128)
    try:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        return (r, g, b)
    except ValueError:
        return (128, 128, 128)


def rgb_distance_normalized(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    """Euclidean distance between two RGB colors, normalized to [0.0, 1.0]."""
    dr = c1[0] - c2[0]
    dg = c1[1] - c2[1]
    db = c1[2] - c2[2]
    # Max possible distance is sqrt(255^2 + 255^2 + 255^2) = ~441.67
    max_dist = math.sqrt(3 * (255 ** 2))
    dist = math.sqrt(dr * dr + dg * dg + db * db)
    return min(1.0, dist / max_dist)


def extract_game_dna_palette_colors(game_dna: Dict[str, Any]) -> List[Tuple[int, int, int]]:
    """Extract RGB color swatches from Game DNA palette object or dict."""
    colors: List[Tuple[int, int, int]] = []
    palette_data = game_dna.get("palette")

    if not palette_data:
        return colors

    if isinstance(palette_data, dict):
        for field in ("primary", "secondary", "accent", "background", "surface"):
            val = palette_data.get(field)
            if isinstance(val, str) and val.startswith("#"):
                colors.append(hex_to_rgb(val))
    elif isinstance(palette_data, list):
        for val in palette_data:
            if isinstance(val, str) and val.startswith("#"):
                colors.append(hex_to_rgb(val))
            elif isinstance(val, (list, tuple)) and len(val) >= 3:
                colors.append((int(val[0]), int(val[1]), int(val[2])))

    return colors


def calculate_palette_deviation(
    image_colors: List[Tuple[int, int, int]],
    dna_colors: List[Tuple[int, int, int]],
) -> float:
    """
    Calculate average minimum distance from image dominant colors to Game DNA target palette.
    Returns 0.0 for identical palette, up to 1.0 for completely opposing colors.
    """
    if not image_colors or not dna_colors:
        return 0.0

    total_min_dist = 0.0
    for img_c in image_colors:
        min_dist = min(rgb_distance_normalized(img_c, dna_c) for dna_c in dna_colors)
        total_min_dist += min_dist

    return total_min_dist / len(image_colors)


def compute_style_token_match(
    style_tokens: List[str],
    text_corpus: List[str],
) -> float:
    """
    Score semantic alignment between Game DNA style tokens and generation prompt/tags.
    Returns normalized float in range [0.00, 1.00].
    """
    if not style_tokens:
        return 1.0

    combined_text = " ".join(text_corpus).lower()
    if not combined_text.strip():
        return 0.5  # Neutral score if no prompt metadata present

    matched_tokens = 0
    total_tokens = len(style_tokens)

    for token in style_tokens:
        token_clean = token.lower().replace("_", " ").strip()
        # Direct phrase match or constituent keywords match
        if token_clean in combined_text:
            matched_tokens += 1
        else:
            subwords = [w for w in re.split(r"[\s_]+", token_clean) if len(w) > 2]
            if subwords and any(w in combined_text for w in subwords):
                matched_tokens += 0.5

    score = min(1.0, max(0.0, matched_tokens / total_tokens))
    return round(score, 3)


class ComfyVisualConsistencyGate(BaseGate):
    """
    Gate: ComfyUI Image Quality & Game DNA Consistency Gate.
    Verifies:
      1. Edge Sharpness / Blur Detection (Laplacian Variance).
      2. Contrast & Exposure Anomalies (crushed black / blown highlights).
      3. Color Palette Alignment against Game DNA palette.
      4. Style Token Consistency Score (0.00 - 1.00).
    """

    gate_name: str = "comfy_visual_consistency_gate"
    gate_version: str = "1.0.0"
    is_fatal: bool = False

    async def evaluate(self, context: GateExecutionContext) -> GateResult:
        artifact = context.artifact or {}
        game_dna = context.game_dna or {}
        media_meta = artifact.get("media_meta", {})
        options = context.options or {}

        artifact_type = str(artifact.get("type", "")).lower()
        if artifact_type in ("manifest", "evaluation_report", "comfy_workflow", "workflow_json"):
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.SKIPPED,
                severity=GateSeverity.INFO,
                score=5.0,
                message=f"Visual consistency gate skipped for non-image artifact type '{artifact_type}'.",
            )

        # Configurable thresholds with Game DNA integration and options precedence
        brand_constraints = game_dna.get("brand_constraints", {})
        visual_thresholds = (
            brand_constraints.get("visual_thresholds")
            or game_dna.get("visual_thresholds")
            or {}
        )

        blur_threshold = float(options.get("blur_threshold", visual_thresholds.get("blur_threshold", 80.0)))
        critical_blur_threshold = float(options.get("critical_blur_threshold", visual_thresholds.get("critical_blur_threshold", 25.0)))
        min_brightness = float(options.get("min_brightness", visual_thresholds.get("min_brightness", 15.0)))
        max_brightness = float(options.get("max_brightness", visual_thresholds.get("max_brightness", 245.0)))
        min_contrast = float(options.get("min_contrast", visual_thresholds.get("min_contrast", 12.0)))
        palette_dev_threshold = float(options.get("palette_deviation_threshold", visual_thresholds.get("palette_deviation_threshold", 0.40)))
        min_style_score = float(options.get("min_style_score", visual_thresholds.get("min_style_score", 0.40)))

        # Metrics to collect
        laplacian_var: Optional[float] = None
        mean_brightness: Optional[float] = None
        contrast_stddev: Optional[float] = None
        image_dominant_colors: List[Tuple[int, int, int]] = []

        # 1. Attempt to load image and calculate metrics via PIL
        pil_img = self._load_pil_image(artifact, media_meta)

        if pil_img is not None:
            # Grayscale conversion for Laplacian and exposure
            gray_img = pil_img.convert("L")
            stat = ImageStat.Stat(gray_img)
            mean_brightness = stat.mean[0]
            contrast_stddev = stat.stddev[0]

            # Laplacian kernel: [0, 1, 0, 1, -4, 1, 0, 1, 0] with offset=128
            lap_kernel = ImageFilter.Kernel((3, 3), [0, 1, 0, 1, -4, 1, 0, 1, 0], scale=1, offset=128)
            lap_img = gray_img.filter(lap_kernel)
            w, h = lap_img.size
            if w > 4 and h > 4:
                # Exclude border pixels to eliminate kernel padding boundary artifacts
                lap_img = lap_img.crop((2, 2, w - 2, h - 2))
            lap_stat = ImageStat.Stat(lap_img)
            laplacian_var = lap_stat.var[0]

            # Dominant colors via thumbnail sampling
            thumb = pil_img.copy().resize((32, 32)).convert("RGB")
            colors = thumb.getcolors(maxcolors=1024)
            if colors:
                # Sort by count descending, pick top 5 colors
                sorted_colors = sorted(colors, key=lambda c: c[0], reverse=True)
                image_dominant_colors = [c[1] for c in sorted_colors[:5]]
        else:
            # Fall back to metadata if precomputed
            if "laplacian_variance" in media_meta:
                laplacian_var = float(media_meta["laplacian_variance"])
            if "mean_brightness" in media_meta:
                mean_brightness = float(media_meta["mean_brightness"])
            if "contrast_stddev" in media_meta:
                contrast_stddev = float(media_meta["contrast_stddev"])
            if "dominant_colors" in media_meta:
                for c in media_meta["dominant_colors"]:
                    if isinstance(c, str) and c.startswith("#"):
                        image_dominant_colors.append(hex_to_rgb(c))
                    elif isinstance(c, (list, tuple)) and len(c) >= 3:
                        image_dominant_colors.append((int(c[0]), int(c[1]), int(c[2])))

        # If still no image metrics available
        if laplacian_var is None and mean_brightness is None:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.WARNING,
                severity=GateSeverity.WARNING,
                score=3.0,
                message="Unable to perform deep visual pixel analysis: Image file or pixel statistics not available in artifact context.",
                details={"media_meta": media_meta},
            )

        # 2. Evaluate Exposure and Contrast (Extreme exposure takes precedence over blur)
        failures: List[str] = []
        warnings: List[str] = []
        failure_codes: List[str] = []

        has_exposure_anomaly = False
        if mean_brightness is not None:
            if mean_brightness < min_brightness:
                has_exposure_anomaly = True
                failures.append(f"Underexposed image / crushed blacks (Mean brightness {mean_brightness:.1f} < {min_brightness}).")
                failure_codes.append("VISUAL_EXPOSURE_ANOMALY")
            elif mean_brightness > max_brightness:
                has_exposure_anomaly = True
                failures.append(f"Overexposed image / blown highlights (Mean brightness {mean_brightness:.1f} > {max_brightness}).")
                failure_codes.append("VISUAL_EXPOSURE_ANOMALY")

        if contrast_stddev is not None and contrast_stddev < min_contrast and not has_exposure_anomaly:
            warnings.append(f"Low image contrast (Stddev {contrast_stddev:.1f} < {min_contrast}).")

        # 3. Evaluate Blurriness / Edge Sharpness (when image has valid exposure range)
        if not has_exposure_anomaly and laplacian_var is not None:
            if laplacian_var < critical_blur_threshold:
                failures.append(f"Severe image blur detected (Laplacian variance {laplacian_var:.1f} < {critical_blur_threshold}).")
                failure_codes.append("VISUAL_BLURRY_OR_DEGRADED")
            elif laplacian_var < blur_threshold:
                warnings.append(f"Image sharpness is borderline blurry (Laplacian variance {laplacian_var:.1f} < {blur_threshold}).")

        # 4. Evaluate Game DNA Color Palette Fidelity
        dna_palette_colors = extract_game_dna_palette_colors(game_dna)
        palette_dev: float = 0.0
        if dna_palette_colors and image_dominant_colors:
            palette_dev = calculate_palette_deviation(image_dominant_colors, dna_palette_colors)
            if palette_dev > palette_dev_threshold:
                warnings.append(f"Color palette deviation exceeds tolerance ({palette_dev:.2f} > {palette_dev_threshold:.2f}).")
                failure_codes.append("PALETTE_DEVIATION_HIGH")

        # 5. Evaluate Style Token Consistency (0.00 - 1.00)
        dna_style_tokens = game_dna.get("style_tokens", [])
        prompt_corpus: List[str] = []
        if "positive_prompt" in media_meta:
            prompt_corpus.append(str(media_meta["positive_prompt"]))
        if "prompt" in media_meta:
            prompt_corpus.append(str(media_meta["prompt"]))
        if "tags" in media_meta and isinstance(media_meta["tags"], list):
            prompt_corpus.extend([str(t) for t in media_meta["tags"]])
        if "style_tokens" in media_meta and isinstance(media_meta["style_tokens"], list):
            prompt_corpus.extend([str(t) for t in media_meta["style_tokens"]])
        if "creative_hypothesis" in context.model_dump():
            hypo = context.creative_hypothesis or {}
            if "intended_hook" in hypo:
                prompt_corpus.append(str(hypo["intended_hook"]))

        style_score = compute_style_token_match(dna_style_tokens, prompt_corpus)
        if dna_style_tokens and style_score < min_style_score:
            warnings.append(f"Style token match score is low ({style_score:.2f} < {min_style_score:.2f}).")
            failure_codes.append("STYLE_MISMATCH")

        # 6. Synthesize Normalized Score (0.00 to 5.00)
        # Component scores [0.0 - 1.0]
        sharp_score = min(1.0, (laplacian_var or 100.0) / 250.0) if laplacian_var is not None else 0.8
        expo_score = 1.0
        if mean_brightness is not None:
            if mean_brightness < min_brightness or mean_brightness > max_brightness:
                expo_score = 0.2
            else:
                expo_score = 1.0 - abs(mean_brightness - 128.0) / 160.0
        contrast_score = min(1.0, (contrast_stddev or 30.0) / 50.0) if contrast_stddev is not None else 0.8
        palette_score = max(0.0, 1.0 - palette_dev)

        weighted_normalized = (
            0.30 * sharp_score
            + 0.25 * expo_score
            + 0.15 * contrast_score
            + 0.15 * palette_score
            + 0.15 * style_score
        )
        final_score = round(max(0.5, min(5.0, weighted_normalized * 5.0)), 2)

        # 7. Formulate GateResult
        details = {
            "laplacian_variance": round(laplacian_var, 2) if laplacian_var is not None else None,
            "mean_brightness": round(mean_brightness, 2) if mean_brightness is not None else None,
            "contrast_stddev": round(contrast_stddev, 2) if contrast_stddev is not None else None,
            "palette_deviation": round(palette_dev, 3),
            "style_token_match_score": style_score,
            "failures": failures,
            "warnings": warnings,
            "failure_codes": failure_codes,
        }

        if failures:
            primary_code = failure_codes[0] if failure_codes else "VISUAL_DEFECT_DETECTED"
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.ERROR,
                score=final_score,
                failure_code=primary_code,
                message="; ".join(failures),
                details=details,
            )

        if warnings:
            primary_code = failure_codes[0] if failure_codes else None
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.WARNING,
                severity=GateSeverity.WARNING,
                score=final_score,
                failure_code=primary_code,
                message="; ".join(warnings),
                details=details,
            )

        return GateResult(
            gate_name=self.gate_name,
            gate_version=self.gate_version,
            status=GateStatus.PASSED,
            severity=GateSeverity.INFO,
            score=final_score,
            message="Image successfully verified: Sharp focus, optimal exposure, and Game DNA consistency satisfied.",
            details=details,
        )

    def _load_pil_image(
        self,
        artifact: Dict[str, Any],
        media_meta: Dict[str, Any],
    ) -> Optional[Any]:
        """Load PIL Image object from bytes, base64, storage reference, or file path."""
        if not HAS_PIL:
            return None

        # 1. Direct PIL instance in memory
        if "pil_image" in media_meta:
            return media_meta["pil_image"]
        if "pil_image" in artifact:
            return artifact["pil_image"]

        # 2. Raw bytes
        if "image_bytes" in media_meta and isinstance(media_meta["image_bytes"], (bytes, bytearray)):
            try:
                return Image.open(io.BytesIO(media_meta["image_bytes"]))
            except Exception as e:
                logger.debug(f"Failed to decode image_bytes: {e}")

        # 3. Base64
        base64_str = media_meta.get("base64_data") or media_meta.get("preview_base64")
        if base64_str and isinstance(base64_str, str):
            try:
                clean_b64 = re.sub(r"^data:image\/[a-zA-Z]+;base64,", "", base64_str.strip())
                raw = base64.b64decode(clean_b64)
                return Image.open(io.BytesIO(raw))
            except Exception as e:
                logger.debug(f"Failed to decode base64 image: {e}")

        # 4. File path or storage_ref
        file_path = media_meta.get("image_path") or artifact.get("storage_ref")
        if file_path and isinstance(file_path, str) and os.path.exists(file_path):
            try:
                return Image.open(file_path)
            except Exception as e:
                logger.debug(f"Failed to read image from disk '{file_path}': {e}")

        return None
