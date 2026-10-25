"""
Gate 1: SchemaGate - Validates artifact output structure, mandatory fields, media metadata, and SHA256 integrity format.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Set
from services.worker_evaluation.gates.base import (
    BaseGate,
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)

VALID_ARTIFACT_TYPES = {
    "image",
    "video",
    "playable_zip",
    "concept_board",
    "evaluation_report",
    "manifest",
}

REQUIRED_CORE_FIELDS = {
    "artifact_id",
    "run_id",
    "type",
    "storage_ref",
    "sha256",
    "bytes",
}

REQUIRED_MEDIA_META_BY_TYPE: Dict[str, Set[str]] = {
    "image": {"width", "height", "format"},
    "video": {"duration_sec", "width", "height"},
    "playable_zip": {"entrypoint"},
    "concept_board": {"concept_id"},
}

SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")


class SchemaGate(BaseGate):
    """Gate 1: Schema & Contract Integrity Gate."""

    gate_name: str = "schema_gate"
    gate_version: str = "1.0.0"
    is_fatal: bool = True

    async def evaluate(self, context: GateExecutionContext) -> GateResult:
        artifact = context.artifact
        if not artifact:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL,
                score=0.0,
                failure_code="SCHEMA_EMPTY_ARTIFACT",
                message="No artifact payload provided for schema evaluation.",
                details={"provided_keys": []},
            )

        # 1. Validate mandatory top-level fields
        missing_fields = REQUIRED_CORE_FIELDS - set(artifact.keys())
        if missing_fields:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL,
                score=0.0,
                failure_code="SCHEMA_MISSING_REQUIRED_FIELD",
                message=f"Missing mandatory artifact fields: {sorted(list(missing_fields))}",
                details={"missing_fields": sorted(list(missing_fields))},
            )

        # 2. Validate artifact type
        artifact_type = str(artifact.get("type", "")).lower()
        if artifact_type not in VALID_ARTIFACT_TYPES:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL,
                score=0.0,
                failure_code="SCHEMA_INVALID_ARTIFACT_TYPE",
                message=f"Invalid artifact type '{artifact_type}'. Must be one of {sorted(list(VALID_ARTIFACT_TYPES))}",
                details={"type": artifact_type, "allowed": sorted(list(VALID_ARTIFACT_TYPES))},
            )

        # 3. Validate SHA256 integrity format
        sha256 = str(artifact.get("sha256", ""))
        if not SHA256_REGEX.match(sha256):
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL,
                score=0.0,
                failure_code="SCHEMA_INVALID_SHA256",
                message=f"Invalid SHA256 format for artifact: '{sha256}'",
                details={"sha256": sha256},
            )

        # 4. Validate byte size
        byte_size = artifact.get("bytes", 0)
        if not isinstance(byte_size, (int, float)) or byte_size <= 0:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL,
                score=0.0,
                failure_code="SCHEMA_INVALID_BYTES",
                message=f"Artifact byte size must be a positive integer, got: {byte_size}",
                details={"bytes": byte_size},
            )

        # 5. Validate media metadata
        media_meta = artifact.get("media_meta")
        if not isinstance(media_meta, dict):
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL,
                score=0.0,
                failure_code="INVALID_MEDIA_METADATA",
                message="Artifact 'media_meta' must be a dictionary.",
                details={"media_meta_type": type(media_meta).__name__},
            )

        expected_meta = REQUIRED_MEDIA_META_BY_TYPE.get(artifact_type, set())
        missing_meta = expected_meta - set(media_meta.keys())
        if missing_meta:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.FATAL,
                score=0.0,
                failure_code="INVALID_MEDIA_METADATA",
                message=f"Missing required media_meta keys for '{artifact_type}': {sorted(list(missing_meta))}",
                details={"missing_keys": sorted(list(missing_meta)), "present_keys": list(media_meta.keys())},
            )

        return GateResult(
            gate_name=self.gate_name,
            gate_version=self.gate_version,
            status=GateStatus.PASSED,
            severity=GateSeverity.INFO,
            score=5.0,
            message=f"Artifact schema, SHA256 integrity and media_meta successfully validated for type '{artifact_type}'.",
            details={
                "artifact_id": artifact.get("artifact_id"),
                "type": artifact_type,
                "bytes": byte_size,
                "media_meta_keys": list(media_meta.keys()),
            },
        )
