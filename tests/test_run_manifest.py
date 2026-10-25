"""Tests for M10 Run Manifest Engine, Frozen Snapshots & Tamper Verification."""

import pytest
from pydantic import ValidationError

from packages.node_registry import WorkflowEdge, WorkflowGraph, WorkflowNode
from services.api.app.modules.workflows import (
    RunManifest,
    RunManifestBuilder,
    WorkflowExecutionService,
)


@pytest.fixture
def sample_graph() -> WorkflowGraph:
    return WorkflowGraph(
        workflow_id="wf_manifest_test",
        nodes=[
            WorkflowNode(id="n1", type="Source Fetch"),
            WorkflowNode(id="n2", type="Genre Classifier"),
        ],
        edges=[
            WorkflowEdge(id="e1", source="n1", target="n2", source_handle="snapshot", target_handle="snapshot"),
        ],
    )


def test_create_manifest_and_sha256_integrity(sample_graph):
    """Verifies frozen manifest assembly and cryptographic SHA256 checksum."""
    manifest = RunManifestBuilder.create_manifest(
        manifest_id="man_001",
        run_id="run_001",
        project_id="proj_alpha",
        workflow_id=sample_graph.workflow_id,
        workflow_version="1.0.0",
        graph_data=sample_graph.model_dump(),
        node_registry_versions={"Source Fetch": "1.0.0", "Genre Classifier": "1.0.0"},
        prompt_versions={"concept_gen_v1": "1.2.0"},
        game_dna_version_id="gp_v3",
        game_dna_data={"genre": "Match-3", "palette": ["#FF0000"]},
        parameters={"seed": 42},
    )

    assert manifest.manifest_id == "man_001"
    assert manifest.run_id == "run_001"
    assert manifest.workflow_graph_hash != ""
    assert len(manifest.manifest_hash) == 64  # Valid SHA256 hex string

    # Verify integrity
    assert RunManifestBuilder.verify_integrity(manifest) is True


def test_manifest_immutability(sample_graph):
    """Verifies that RunManifest cannot be mutated in-place once frozen."""
    manifest = RunManifestBuilder.create_manifest(
        manifest_id="man_frozen",
        run_id="run_frozen",
        project_id="proj_alpha",
        workflow_id=sample_graph.workflow_id,
        workflow_version="1.0.0",
        graph_data=sample_graph.model_dump(),
    )

    # Attempting to alter any frozen attribute must raise ValidationError
    with pytest.raises(ValidationError):
        manifest.workflow_version = "2.0.0"  # type: ignore


def test_tamper_detection(sample_graph):
    """Verifies that any altered field causes verify_integrity to return False."""
    manifest = RunManifestBuilder.create_manifest(
        manifest_id="man_tamper",
        run_id="run_tamper",
        project_id="proj_alpha",
        workflow_id=sample_graph.workflow_id,
        workflow_version="1.0.0",
        graph_data=sample_graph.model_dump(),
    )

    # Valid manifest passes
    assert RunManifestBuilder.verify_integrity(manifest) is True

    # Tampered manifest with altered parameter but original stored hash fails
    tampered_data = manifest.model_dump()
    tampered_data["parameters"] = {"tampered_key": "injected_value"}
    tampered_manifest = RunManifest(**tampered_data)

    assert RunManifestBuilder.verify_integrity(tampered_manifest) is False


@pytest.mark.asyncio
async def test_workflow_execution_service_lifecycle(sample_graph):
    """Verifies end-to-end integration with WorkflowExecutionService."""
    service = WorkflowExecutionService()
    service.register_graph(sample_graph)

    manifest = await service.start_run(
        workflow_id=sample_graph.workflow_id,
        project_id="proj_test_service",
        parameters={"campaign": "autumn_burst"},
    )

    assert manifest.run_id.startswith("run_")
    retrieved = service.get_manifest(manifest.run_id)
    assert retrieved is not None
    assert retrieved.manifest_id == manifest.manifest_id
    assert RunManifestBuilder.verify_integrity(retrieved) is True
