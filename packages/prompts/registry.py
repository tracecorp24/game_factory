"""
Prompt Registry and Template Engine.
Provides deterministic, versioned, and immutable prompt templates.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PromptVersion(BaseModel):
    template_id: str
    version: str
    system_prompt: str
    user_prompt_template: str
    input_variables: List[str] = Field(default_factory=list)
    description: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sha256: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.sha256:
            raw = f"{self.template_id}:{self.version}:{self.system_prompt}:{self.user_prompt_template}"
            self.sha256 = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def render(self, **kwargs: Any) -> Dict[str, str]:
        """Render system and user prompt with provided parameters."""
        missing = [var for var in self.input_variables if var not in kwargs]
        if missing:
            raise ValueError(f"Missing required prompt variables: {missing}")

        try:
            rendered_user = self.user_prompt_template.format(**kwargs)
        except KeyError as exc:
            raise ValueError(f"Template variable not supplied: {exc}") from exc

        return {
            "template_id": self.template_id,
            "version": self.version,
            "sha256": self.sha256,
            "system_prompt": self.system_prompt,
            "user_prompt": rendered_user,
        }


class PromptTemplate(BaseModel):
    template_id: str
    name: str
    description: str
    default_version: str
    versions: Dict[str, PromptVersion] = Field(default_factory=dict)

    def get_version(self, version: Optional[str] = None) -> PromptVersion:
        ver_key = version or self.default_version
        if ver_key not in self.versions:
            raise KeyError(f"Prompt template '{self.template_id}' has no version '{ver_key}'")
        return self.versions[ver_key]


class PromptRegistry:
    """Central registry of versioned prompt templates."""

    _templates: Dict[str, PromptTemplate] = {}

    @classmethod
    def register(cls, template: PromptTemplate) -> None:
        cls._templates[template.template_id] = template

    @classmethod
    def register_version(cls, template_id: str, version: PromptVersion) -> None:
        if template_id not in cls._templates:
            cls._templates[template_id] = PromptTemplate(
                template_id=template_id,
                name=template_id,
                description=version.description,
                default_version=version.version,
                versions={version.version: version},
            )
        else:
            cls._templates[template_id].versions[version.version] = version

    @classmethod
    def get(cls, template_id: str, version: Optional[str] = None) -> PromptVersion:
        if template_id not in cls._templates:
            raise KeyError(f"Template '{template_id}' is not registered in PromptRegistry")
        return cls._templates[template_id].get_version(version)

    @classmethod
    def list_templates(cls) -> List[Dict[str, Any]]:
        return [
            {
                "template_id": t.template_id,
                "name": t.name,
                "default_version": t.default_version,
                "versions": list(t.versions.keys()),
            }
            for t in cls._templates.values()
        ]
