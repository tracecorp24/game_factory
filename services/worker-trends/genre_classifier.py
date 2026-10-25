"""
Genre and Mechanic Pattern Classifier.
Categorizes games and creative observations into standardized taxonomy.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    primary_genre: str
    subgenres: List[str] = Field(default_factory=list)
    mechanic_patterns: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    matched_rules: List[str] = Field(default_factory=list)
    is_human_corrected: bool = False
    rationale: str = ""


class GenreClassifier:
    """
    Deterministic rule-based and regex classifier with LLM fallback support.
    Provides human-correctable taxonomy tagging for market intelligence.
    """

    GENRE_RULES: Dict[str, Dict[str, Any]] = {
        "Match-3": {
            "keywords": ["match 3", "match-3", "match three", "swap and match", "tile match", "blast", "crush", "candy", "royal", "saga", "jewel"],
            "subgenres": ["Tile Matching", "Cascade Puzzle", "Collapse"],
            "mechanics": ["grid_matching", "chain_reaction", "line_clear", "move_limit"],
        },
        "Merge": {
            "keywords": ["merge", "merge 2", "merge mansion", "merge dragons", "combine items", "merge garden", "synthesize"],
            "subgenres": ["Merge 2", "Merge 3", "Board Evolution"],
            "mechanics": ["merge_2", "generator_spawner", "board_expansion", "energy_cooldown"],
        },
        "Sorting": {
            "keywords": ["sort", "water sort", "goods sort", "ball sort", "color sort", "organize shelves", "tube puzzle"],
            "subgenres": ["Goods Sorting", "Color Liquid", "Inventory Organization"],
            "mechanics": ["color_sorting", "tube_capacity", "visual_order", "satisfying_organization"],
        },
        "Puzzle": {
            "keywords": ["puzzle", "brain teaser", "pin pull", "save the dog", "draw to save", "logic test", "riddle"],
            "subgenres": ["Physics Logic", "Dilemma / Rescue", "Line Drawing"],
            "mechanics": ["pull_the_pin", "rescue_hero", "physics_draw", "fail_fail_retry"],
        },
        "Idle RPG": {
            "keywords": ["idle", "afk", "rpg", "auto battle", "summon", "hero collector", "dungeon crawl", "gacha"],
            "subgenres": ["Hero Collector", "AFK Battler", "Roguelite Idle"],
            "mechanics": ["idle_progression", "auto_combat", "hero_ascension", "loot_drop"],
        },
        "Strategy 4X": {
            "keywords": ["empire", "conquer", "4x", "war", "build kingdom", "survival shelter", "alliance", "troops"],
            "subgenres": ["Survival 4X", "Medieval Empire", "Sci-Fi Colony"],
            "mechanics": ["base_building", "troop_march", "territory_expansion", "alliance_war"],
        },
        "Hypercasual": {
            "keywords": ["runner", "stack", "count master", "crowd", "satisfying", "simple controls", "hypercasual", "one tap"],
            "subgenres": ["Multiplier Runner", "Stacking", "ASMR Slicing"],
            "mechanics": ["runner_obstacle", "multiplier_gates", "one_touch", "instant_restart"],
        },
        "Simulation": {
            "keywords": ["tycoon", "simulator", "manage restaurant", "cooking", "hotel", "supermarket", "renovate", "makeover"],
            "subgenres": ["Time Management", "Decor Renovation", "Business Tycoon"],
            "mechanics": ["customer_flow", "station_upgrades", "room_makeover", "task_checklist"],
        },
    }

    def __init__(self, custom_rules: Optional[Dict[str, Dict[str, Any]]] = None):
        self.rules = dict(self.GENRE_RULES)
        if custom_rules:
            self.rules.update(custom_rules)

    def classify_text(
        self,
        text: str,
        category_hint: Optional[str] = None,
        human_override: Optional[Dict[str, Any]] = None,
    ) -> ClassificationResult:
        """
        Classifies given text into genre, subgenres, and mechanics.
        Allows human override dictionary to take absolute precedence.
        """
        if human_override:
            return ClassificationResult(
                primary_genre=human_override.get("primary_genre", "Unknown"),
                subgenres=human_override.get("subgenres", []),
                mechanic_patterns=human_override.get("mechanic_patterns", []),
                confidence=1.0,
                matched_rules=["human_override"],
                is_human_corrected=True,
                rationale=human_override.get("rationale", "Manually specified by operator"),
            )

        search_corpus = text.lower()
        if category_hint:
            search_corpus += " " + category_hint.lower()

        scores: Dict[str, Tuple[int, List[str]]] = {}
        for genre, conf in self.rules.items():
            matches: List[str] = []
            for kw in conf["keywords"]:
                pattern = r"\b" + re.escape(kw) + r"\b"
                if re.search(pattern, search_corpus):
                    matches.append(kw)
            scores[genre] = (len(matches), matches)

        # Find genre with highest match count
        sorted_scores = sorted(scores.items(), key=lambda item: item[1][0], reverse=True)
        best_genre, (best_count, best_matches) = sorted_scores[0]

        if best_count > 0:
            genre_def = self.rules[best_genre]
            confidence = min(1.0, 0.4 + (best_count * 0.2))
            return ClassificationResult(
                primary_genre=best_genre,
                subgenres=genre_def.get("subgenres", []),
                mechanic_patterns=genre_def.get("mechanics", []),
                confidence=round(confidence, 2),
                matched_rules=best_matches,
                rationale=f"Matched keywords: {', '.join(best_matches)}",
            )

        # Fallback to category hint or Puzzle default
        if category_hint and category_hint in self.rules:
            genre_def = self.rules[category_hint]
            return ClassificationResult(
                primary_genre=category_hint,
                subgenres=genre_def.get("subgenres", []),
                mechanic_patterns=genre_def.get("mechanics", []),
                confidence=0.45,
                matched_rules=["category_hint"],
                rationale=f"Inferred from store category hint '{category_hint}'",
            )

        return ClassificationResult(
            primary_genre="Casual Puzzle",
            subgenres=["General Casual"],
            mechanic_patterns=["grid_interaction", "puzzle_solving"],
            confidence=0.30,
            matched_rules=["default_fallback"],
            rationale="No definitive keywords found; defaulted to general Casual Puzzle",
        )
