"""
Python alias and direct re-export module for packages.comfy-bridge.
"""

import importlib
import sys

_real_pkg = importlib.import_module("packages.comfy-bridge")

for _k, _v in _real_pkg.__dict__.items():
    if not _k.startswith("__"):
        globals()[_k] = _v

__all__ = getattr(_real_pkg, "__all__", [])
