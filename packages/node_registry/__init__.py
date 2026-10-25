"""Python alias module for packages.node-registry."""

import importlib
import sys

_real_pkg = importlib.import_module("packages.node-registry")

for _k, _v in _real_pkg.__dict__.items():
    if not _k.startswith("__"):
        globals()[_k] = _v

__all__ = getattr(_real_pkg, "__all__", [])
