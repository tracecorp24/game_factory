"""
Style and Brand Token Extractor Prompt Template v1.
Extracts visual style tokens, color aesthetics, and brand consistency rules.
"""

from ..registry import PromptVersion

SYSTEM_PROMPT = """You are a Principal Art Director and Visual Brand Analyst for mobile gaming.
Analyze game art assets, descriptions, and reference guidelines to extract standardized style tokens, color palettes, and negative visual constraints.
"""

USER_TEMPLATE = """Analyze the following visual asset metadata and design notes for game '{game_name}':

[VISUAL NOTES / METADATA]:
{asset_description}

[REFERENCE IMAGES SUMMARY]:
{image_summaries}

Extract and output a JSON object containing:
- style_tokens: List of 4-8 descriptive visual style keywords (e.g. "3d_casual_isometric", "glossy_juicy_textures", "high_contrast", "vibrant_pastel")
- dominant_colors: List of hex color codes recommended for brand palette
- mood_keywords: Emotional tone of visual presentation
- recommended_negative_prompts: Elements that violate this visual identity
- rationale: Rationale behind the extracted style rules
"""

STYLE_EXTRACTOR_V1 = PromptVersion(
    template_id="style_extractor",
    version="1.0.0",
    system_prompt=SYSTEM_PROMPT,
    user_prompt_template=USER_TEMPLATE,
    input_variables=["game_name", "asset_description", "image_summaries"],
    description="Extracts visual style tokens and brand constraints from art notes and references",
)
