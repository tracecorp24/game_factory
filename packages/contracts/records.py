"""
Execution ledger, accounting, and artifact records for CreativeForge v3.0.
"""
from datetime import datetime
import hashlib
import json
from typing import Any, Dict, Literal, Optional
from pydantic import Field, model_validator

from packages.contracts.common import BaseContractModel, generate_uuid, utc_now


UsageSource = Literal["provider_reported", "estimated", "invoice_reconciled", "missing"]
CostKind = Literal["llm_token", "image_generation", "video_generation", "compute_second"]
CostStatus = Literal["estimated", "actual", "reconciled"]
ArtifactType = Literal["image", "video", "playable_zip", "concept_board", "evaluation_report", "manifest"]


class TokenUsageRecord(BaseContractModel):
    """
    Standard token usage accounting record.
    Adheres strictly to the 'No double-counting' rule:
    cached_input_tokens are reported separately and not counted twice if provider includes them in input_tokens.
    """
    input_tokens: int = Field(default=0, ge=0, description="Total input/prompt tokens")
    output_tokens: int = Field(default=0, ge=0, description="Total generated completion tokens")
    total_tokens: int = Field(default=0, ge=0, description="Total billable tokens")
    cached_input_tokens: Optional[int] = Field(default=None, ge=0, description="Cached prompt tokens if supported")
    cache_creation_tokens: Optional[int] = Field(default=None, ge=0, description="Cache write/creation tokens")
    reasoning_tokens: Optional[int] = Field(default=None, ge=0, description="Internal reasoning/thinking tokens")

    billable_input_units: float = Field(default=0.0, ge=0.0, description="Weighted billable input units")
    billable_output_units: float = Field(default=0.0, ge=0.0, description="Weighted billable output units")
    billable_media_units: float = Field(default=0.0, ge=0.0, description="Image/video non-token billable units")

    usage_source: UsageSource = Field(..., description="Source of usage figures")

    @model_validator(mode="after")
    def validate_totals(self) -> "TokenUsageRecord":
        if self.total_tokens == 0 and (self.input_tokens > 0 or self.output_tokens > 0):
            # Auto-calculate total if not explicitly set
            self.total_tokens = self.input_tokens + self.output_tokens
        return self


class CostEntryRecord(BaseContractModel):
    """
    Financial ledger entry for LLM calls, image/video generations, and compute resources.
    Unknown costs must be flagged with status='estimated' or tracked explicitly, never assumed $0.
    """
    cost_id: str = Field(default_factory=generate_uuid, description="Unique cost entry identifier")
    amount: float = Field(..., ge=0.0, description="Cost amount in specified currency")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="ISO 4217 Currency code")
    cost_kind: CostKind = Field(..., description="Category of resource incurred")
    status: CostStatus = Field(..., description="Accounting state: estimated, actual, or reconciled")
    invocation_id: Optional[str] = Field(default=None, description="Linked model invocation ID")
    usage_record_id: Optional[str] = Field(default=None, description="Linked usage record ID")
    price_version_id: Optional[str] = Field(default=None, description="Price catalog version ID applied")
    created_at: datetime = Field(default_factory=utc_now, description="Recording timestamp")


class ArtifactRecord(BaseContractModel):
    """
    Metadata representation of an immutable stored artifact.
    Large binaries remain in object storage; this record tracks the pointer and checksum.
    """
    artifact_id: str = Field(default_factory=generate_uuid, description="Unique artifact identifier")
    run_id: str = Field(..., description="Run identifier producing this artifact")
    type: ArtifactType = Field(..., description="Artifact category")
    storage_ref: str = Field(..., description="URI or path in object store (e.g. s3://... or local://...)")
    sha256: str = Field(..., description="SHA256 hex digest of artifact contents")
    bytes: int = Field(..., ge=0, description="Exact file size in bytes")
    media_meta: Dict[str, Any] = Field(default_factory=dict, description="Dimensions, format, duration, fps metadata")
    created_at: datetime = Field(default_factory=utc_now, description="Creation timestamp")


class RunManifestRecord(BaseContractModel):
    """
    M10 - Reproducibility & Frozen Execution Manifest.
    Captures exact versions, input hashes, and environment parameters for deterministic audit.
    """
    manifest_id: str = Field(default_factory=generate_uuid, description="Unique manifest identifier")
    run_id: str = Field(..., description="Run identifier")
    workflow_version_id: str = Field(..., description="Frozen workflow template version ID")
    game_profile_version_id: Optional[str] = Field(default=None, description="Frozen Game DNA profile version ID")
    prompt_versions: Dict[str, str] = Field(default_factory=dict, description="Map of prompt_name -> version_id")
    model_versions: Dict[str, str] = Field(default_factory=dict, description="Map of agent/task -> model_id")
    input_hashes: Dict[str, str] = Field(default_factory=dict, description="SHA256 hashes of all input files/briefs")
    environment: Dict[str, Any] = Field(default_factory=dict, description="Runtime environment versions and settings")
    code_commit: Optional[str] = Field(default=None, description="Git commit hash of repository")
    created_at: datetime = Field(default_factory=utc_now, description="Creation timestamp")
    sha256: str = Field(default="", description="SHA256 digest of manifest contents")

    @classmethod
    def create_manifest(
        cls,
        run_id: str,
        workflow_version_id: str,
        game_profile_version_id: Optional[str] = None,
        prompt_versions: Optional[Dict[str, str]] = None,
        model_versions: Optional[Dict[str, str]] = None,
        input_hashes: Optional[Dict[str, str]] = None,
        environment: Optional[Dict[str, Any]] = None,
        code_commit: Optional[str] = None,
    ) -> "RunManifestRecord":
        prompts = prompt_versions or {}
        models = model_versions or {}
        inputs = input_hashes or {}
        env = environment or {}
        mid = generate_uuid()
        now = utc_now()

        content = {
            "run_id": run_id,
            "workflow_version_id": workflow_version_id,
            "game_profile_version_id": game_profile_version_id,
            "prompt_versions": prompts,
            "model_versions": models,
            "input_hashes": inputs,
            "environment": env,
            "code_commit": code_commit,
        }
        raw_repr = json.dumps(content, sort_keys=True)
        manifest_hash = f"sha256:{hashlib.sha256(raw_repr.encode('utf-8')).hexdigest()}"

        return cls(
            manifest_id=mid,
            run_id=run_id,
            workflow_version_id=workflow_version_id,
            game_profile_version_id=game_profile_version_id,
            prompt_versions=prompts,
            model_versions=models,
            input_hashes=inputs,
            environment=env,
            code_commit=code_commit,
            created_at=now,
            sha256=manifest_hash,
        )
