"""
Genre Classifier Prompt Template v1.
Classifies games and ads into taxonomy genres, subgenres, and mechanic patterns.
"""

from ..registry import PromptVersion

SYSTEM_PROMPT = """You are an expert mobile gaming taxonomy analyst at CreativeForge Studio.
Your role is to classify raw app store listings, descriptions, and creative transcriptions into verified genres, mechanics patterns, and hook archetypes.
Output must be strictly valid JSON.
"""

USER_TEMPLATE = """Classify the following mobile game asset / listing:

[TITLE]: {app_title}
[DESCRIPTION / TEXT]: {description}
[CATEGORIES / TAGS]: {tags}

Provide a JSON object with:
- primary_genre: Primary genre from (Match-3, Merge, Sorting, Puzzle, Idle RPG, Strategy 4X, Hypercasual, Simulation, Action, Runner)
- subgenres: List of subgenres
- mechanic_patterns: List of recognized mechanic patterns (e.g. grid_matching, line_clear, chain_reaction, time_pressure, pull_pin, sorting_tubes, merge_2)
- confidence: Float between 0.0 and 1.0
- rationale: Explanation for classification
"""

GENRE_CLASSIFIER_V1 = PromptVersion(
    template_id="genre_classifier",
    version="1.0.0",
    system_prompt=SYSTEM_PROMPT,
    user_prompt_template=USER_TEMPLATE,
    input_variables=["app_title", "description", "tags"],
    description="Classifies game descriptions into standardized genres and mechanic patterns",
)
