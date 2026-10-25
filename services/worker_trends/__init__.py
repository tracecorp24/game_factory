"""Python alias package for services.worker-trends."""

import os
import sys

_real_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "worker-trends"))
__path__ = [_real_dir]

import importlib
_real_pkg = importlib.import_module("services.worker-trends")

for _k, _v in _real_pkg.__dict__.items():
    if not _k.startswith("__"):
        globals()[_k] = _v

__all__ = getattr(_real_pkg, "__all__", [])
