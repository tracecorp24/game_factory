"""
CreativeForge Intelligence Studio v3.0 - Prompts Package
Versioned prompt templates and registry for AI Agent tasks.
"""

from .registry import PromptRegistry, PromptTemplate, PromptVersion
from . import templates

__all__ = ["PromptRegistry", "PromptTemplate", "PromptVersion", "templates"]
