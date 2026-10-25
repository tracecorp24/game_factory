"""Python alias module for services.worker-orchestrator."""

import importlib

_real_pkg = importlib.import_module("services.worker-orchestrator")

for _k, _v in _real_pkg.__dict__.items():
    if not _k.startswith("__"):
        globals()[_k] = _v

__all__ = getattr(_real_pkg, "__all__", [])
