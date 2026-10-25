"""
Admin, Model Policies, Data Retention and Audit Log REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J & Module N.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="", tags=["Admin & Security"])

_MODEL_POLICIES: Dict[str, Any] = {
    "default_policy": {
        "id": "policy_v1",
        "allowed_providers": ["openai", "anthropic", "self_hosted"],
        "max_cost_per_run_usd": 15.0,
        "enforce_json_schema": True,
        "fallback_model_map": {
            "gpt-4o": "claude-3-5-sonnet",
            "claude-3-5-sonnet": "gpt-4o-mini",
        },
    }
}

_RETENTION_POLICIES: Dict[str, Any] = {
    "default_retention": {
        "event_ledger_retention_days": 365,
        "raw_snapshots_retention_days": 90,
        "transient_artifacts_retention_days": 30,
        "pii_redaction_level": "sanitized",
    }
}

_AUDIT_LOGS: List[Dict[str, Any]] = [
    {
        "id": "aud_01",
        "actor_id": "usr_system",
        "action": "POLICY_INITIALIZE",
        "entity_type": "model_policy",
        "entity_id": "policy_v1",
        "created_at": "2026-10-25T10:00:00Z",
    }
]


class ModelPolicyUpdate(BaseModel):
    allowed_providers: Optional[List[str]] = None
    max_cost_per_run_usd: Optional[float] = None
    enforce_json_schema: Optional[bool] = None
    fallback_model_map: Optional[Dict[str, str]] = None


class RetentionPolicyUpdate(BaseModel):
    event_ledger_retention_days: Optional[int] = None
    raw_snapshots_retention_days: Optional[int] = None
    transient_artifacts_retention_days: Optional[int] = None
    pii_redaction_level: Optional[str] = None


@router.get("/model-policies")
async def get_model_policies():
    """Get active model policies and cost bounds."""
    return _MODEL_POLICIES["default_policy"]


@router.put("/model-policies")
async def update_model_policies(payload: ModelPolicyUpdate):
    """Update active model policies and budget ceilings."""
    current = _MODEL_POLICIES["default_policy"]
    if payload.allowed_providers is not None:
        current["allowed_providers"] = payload.allowed_providers
    if payload.max_cost_per_run_usd is not None:
        current["max_cost_per_run_usd"] = payload.max_cost_per_run_usd
    if payload.enforce_json_schema is not None:
        current["enforce_json_schema"] = payload.enforce_json_schema
    if payload.fallback_model_map is not None:
        current["fallback_model_map"] = payload.fallback_model_map
    return current


@router.get("/retention")
async def get_retention_policy():
    """Get data retention and PII redaction rules."""
    return _RETENTION_POLICIES["default_retention"]


@router.put("/retention")
async def update_retention_policy(payload: RetentionPolicyUpdate):
    """Update data retention and PII redaction rules."""
    current = _RETENTION_POLICIES["default_retention"]
    if payload.event_ledger_retention_days is not None:
        current["event_ledger_retention_days"] = payload.event_ledger_retention_days
    if payload.raw_snapshots_retention_days is not None:
        current["raw_snapshots_retention_days"] = payload.raw_snapshots_retention_days
    if payload.transient_artifacts_retention_days is not None:
        current["transient_artifacts_retention_days"] = payload.transient_artifacts_retention_days
    if payload.pii_redaction_level is not None:
        current["pii_redaction_level"] = payload.pii_redaction_level
    return current


@router.get("/audit")
async def list_audit_events(limit: int = 50):
    """Query append-only audit event log."""
    return _AUDIT_LOGS[:limit]
