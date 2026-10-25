"""
Prompt templates collection.
"""

from .ideation_v1 import IDEATION_V1
from .genre_classifier_v1 import GENRE_CLASSIFIER_V1
from .style_extractor_v1 import STYLE_EXTRACTOR_V1
from .mechanic_validator_v1 import MECHANIC_VALIDATOR_V1
from .heuristic_ranking_v1 import HEURISTIC_RANKING_V1
from .learning_synthesis_v1 import LEARNING_SYNTHESIS_V1

from ..registry import PromptRegistry

# Automatically register built-in templates
PromptRegistry.register_version("ideation", IDEATION_V1)
PromptRegistry.register_version("genre_classifier", GENRE_CLASSIFIER_V1)
PromptRegistry.register_version("style_extractor", STYLE_EXTRACTOR_V1)
PromptRegistry.register_version("mechanic_validator", MECHANIC_VALIDATOR_V1)
PromptRegistry.register_version("heuristic_ranking", HEURISTIC_RANKING_V1)
PromptRegistry.register_version("learning_synthesis", LEARNING_SYNTHESIS_V1)

__all__ = [
    "IDEATION_V1",
    "GENRE_CLASSIFIER_V1",
    "STYLE_EXTRACTOR_V1",
    "MECHANIC_VALIDATOR_V1",
    "HEURISTIC_RANKING_V1",
    "LEARNING_SYNTHESIS_V1",
]
