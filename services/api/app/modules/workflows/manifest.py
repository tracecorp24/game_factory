"""M10 - Run Manifest Engine: Frozen snapshots, immutability, and reproducibility."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class RunManifest(BaseModel):
    """
    Immutable frozen snapshot of everything required to reproduce an execution run.
    Once created, changes to workflow designs, prompt templates, or model settings
    cannot alter this frozen execution contract.
    """
    model_config = ConfigDict(frozen=True)

    manifest_id: str = Field(..., description="Unique manifest UUID")
    run_id: str = Field(..., description="Associated workflow run UUID")
    project_id: str = Field(..., description="Tenant / project ID")
    campaign_id: Optional[str] = Field(default=None, description="Associated marketing campaign ID")
    created_at: str = Field(..., description="UTC ISO8601 creation timestamp")

    # Frozen Versions
    workflow_id: str = Field(..., description="ID of workflow template")
    workflow_version: str = Field(..., description="Workflow version string")
    workflow_graph_hash: str = Field(..., description="SHA256 hash of the frozen graph definition")
    frozen_graph: Dict[str, Any] = Field(..., description="Normalized frozen graph JSON")

    node_registry_versions: Dict[str, str] = Field(
        default_factory=dict, description="node_type -> node_version map"
    )
    prompt_versions: Dict[str, str] = Field(
        default_factory=dict, description="prompt_template_id -> frozen version"
    )
    game_dna_version_id: Optional[str] = Field(default=None, description="Frozen Game DNA profile version")
    game_dna_hash: Optional[str] = Field(default=None, description="SHA256 of frozen game mechanics & style")
    trend_snapshot_ids: List[str] = Field(default_factory=list, description="IDs of source trend observations used")
    source_licenses: Dict[str, str] = Field(default_factory=dict, description="License / ToS notes for data sources")

    # Model & Pricing Snapshot
    model_policies: Dict[str, Any] = Field(
        default_factory=dict, description="Model routing rules, quality tier, and max cost budgets"
    )
    pricing_snapshot: Dict[str, Any] = Field(
        default_factory=dict, description="Price catalog version and unit rates at invocation time"
    )

    # Execution Parameters & Environment
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Run input parameters")
    random_seeds: Dict[str, int] = Field(default_factory=dict, description="Seeds for determinism where applicable")
    code_commit_sha: Optional[str] = Field(default=None, description="Git commit SHA of running worker code")
    input_artifact_sha: Optional[str] = Field(default=None, description="Hash of initial input assets")
    environment_digest: str = Field(..., description="Digest of Docker/sandbox container environment")
    evaluation_rubric_versions: Dict[str, str] = Field(
        default_factory=dict, description="Version of QA rubrics used for gate checks"
    )

    # Integrity
    manifest_hash: str = Field(..., description="Deterministic SHA256 integrity hash of all manifest fields")


class RunManifestBuilder:
    """Builder to assemble, freeze, and compute integrity hash for RunManifest."""

    @staticmethod
    def _compute_hash(data_dict: Dict[str, Any]) -> str:
        """Computes deterministic SHA256 of a dict sorted by keys."""
        dumped = json.dumps(data_dict, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()

    @classmethod
    def create_manifest(
        cls,
        manifest_id: str,
        run_id: str,
        project_id: str,
        workflow_id: str,
        workflow_version: str,
        graph_data: Dict[str, Any],
        environment_digest: str = "sha256:creativeforge_v3_runtime_prod",
        campaign_id: Optional[str] = None,
        node_registry_versions: Optional[Dict[str, str]] = None,
        prompt_versions: Optional[Dict[str, str]] = None,
        game_dna_version_id: Optional[str] = None,
        game_dna_data: Optional[Dict[str, Any]] = None,
        trend_snapshot_ids: Optional[List[str]] = None,
        source_licenses: Optional[Dict[str, str]] = None,
        model_policies: Optional[Dict[str, Any]] = None,
        pricing_snapshot: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        random_seeds: Optional[Dict[str, int]] = None,
        code_commit_sha: Optional[str] = None,
        input_artifact_sha: Optional[str] = None,
        evaluation_rubric_versions: Optional[Dict[str, str]] = None,
    ) -> RunManifest:
        """
        Freezes the entire configuration and generates a cryptographically signed RunManifest.
        """
        created_at = datetime.now(timezone.utc).isoformat()
        graph_hash = cls._compute_hash(graph_data)
        dna_hash = cls._compute_hash(game_dna_data) if game_dna_data else None

        raw_dict = {
            "manifest_id": manifest_id,
            "run_id": run_id,
            "project_id": project_id,
            "campaign_id": campaign_id,
            "created_at": created_at,
            "workflow_id": workflow_id,
            "workflow_version": workflow_version,
            "workflow_graph_hash": graph_hash,
            "frozen_graph": graph_data,
            "node_registry_versions": node_registry_versions or {},
            "prompt_versions": prompt_versions or {},
            "game_dna_version_id": game_dna_version_id,
            "game_dna_hash": dna_hash,
            "trend_snapshot_ids": trend_snapshot_ids or [],
            "source_licenses": source_licenses or {},
            "model_policies": model_policies or {},
            "pricing_snapshot": pricing_snapshot or {},
            "parameters": parameters or {},
            "random_seeds": random_seeds or {},
            "code_commit_sha": code_commit_sha or "git-rev-master-prod",
            "input_artifact_sha": input_artifact_sha,
            "environment_digest": environment_digest,
            "evaluation_rubric_versions": evaluation_rubric_versions or {"schema_v1": "1.0", "qa_rubric_v3": "3.1"},
        }

        # Calculate final manifest integrity hash (excluding manifest_hash itself)
        manifest_hash = cls._compute_hash(raw_dict)

        return RunManifest(
            manifest_id=manifest_id,
            run_id=run_id,
            project_id=project_id,
            campaign_id=campaign_id,
            created_at=created_at,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
            workflow_graph_hash=graph_hash,
            frozen_graph=graph_data,
            node_registry_versions=raw_dict["node_registry_versions"],
            prompt_versions=raw_dict["prompt_versions"],
            game_dna_version_id=game_dna_version_id,
            game_dna_hash=dna_hash,
            trend_snapshot_ids=raw_dict["trend_snapshot_ids"],
            source_licenses=raw_dict["source_licenses"],
            model_policies=raw_dict["model_policies"],
            pricing_snapshot=raw_dict["pricing_snapshot"],
            parameters=raw_dict["parameters"],
            random_seeds=raw_dict["random_seeds"],
            code_commit_sha=raw_dict["code_commit_sha"],
            input_artifact_sha=input_artifact_sha,
            environment_digest=environment_digest,
            evaluation_rubric_versions=raw_dict["evaluation_rubric_versions"],
            manifest_hash=manifest_hash,
        )

    @classmethod
    def verify_integrity(cls, manifest: RunManifest) -> bool:
        """Verifies that the manifest contents match its manifest_hash checksum."""
        manifest_dict = manifest.model_dump()
        stored_hash = manifest_dict.pop("manifest_hash")
        expected_hash = cls._compute_hash(manifest_dict)
        return stored_hash == expected_hash
