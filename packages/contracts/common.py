"""
Common utilities and base schemas for CreativeForge contracts.
"""
from datetime import datetime, timezone
import hashlib
import json
import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


def generate_uuid() -> str:
    """Generate a standard UUID4 string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def compute_sha256(data: Any) -> str:
    """Compute SHA256 hex digest for string, bytes, or dict/list object."""
    if isinstance(data, (dict, list)):
        payload_bytes = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    elif isinstance(data, str):
        payload_bytes = data.encode("utf-8")
    elif isinstance(data, bytes):
        payload_bytes = data
    else:
        payload_bytes = str(data).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload_bytes).hexdigest()}"


class BaseContractModel(BaseModel):
    """Base Pydantic v2 model with strict serialization and standard config."""
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
    )
