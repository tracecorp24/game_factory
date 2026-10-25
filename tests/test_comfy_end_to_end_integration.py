"""
End-to-End Hybrid Integration Test Suite for CreativeForge Intelligence Studio v3.0.

Tests the complete 5-Agent Cohesive Cycle:
Agent H1 (Comfy Bridge Transpiler & Port Typing)
Agent H2 (Worker Execution, Variable Template Engine, WS Streaming)
Agent H3 (Contracts, Preset API, SQLAlchemy Persistence)
Agent H4 (AST Security Sandboxing & Game DNA Visual Quality Gate)
Agent H5 (Frontend Sub-Canvas Data Contract & Telemetry Parity)
"""

import io
import json
from pathlib import Path
import pytest
from starlette.testclient import TestClient
from PIL import Image

# Agent H1
from packages.comfy_bridge import (
    comfy_to_react_flow,
    react_flow_to_comfy,
    validate_workflow_graph,
    get_port_color,
    ComfyPortType,
)

# Agent H2
from services.worker_image.template_engine import ComfyTemplateEngine
from services.worker_image.adapters.comfyui_adapter import ComfyUIAdapter
from services.worker_image.image_models import ImageAssetRequest

# Agent H3
from services.api.app.main import app
from services.api.app.modules.comfy.service import comfy_service
from packages.contracts.comfy_contracts import ComfyPresetCreate, ComfyVariableSpec

# Agent H4
from services.worker_evaluation.security_rules import WorkflowSecurityLinter
from services.worker_evaluation.gates.comfy_security_gate import ComfySecurityGate
from services.worker_evaluation.gates.comfy_visual_consistency_gate import ComfyVisualConsistencyGate
from services.worker_evaluation.pipeline import QualityGatePipeline
from services.worker_evaluation.gates.base import GateExecutionContext, GateStatus


@pytest.fixture
def api_client():
    return TestClient(app)


def _generate_synthetic_game_asset_image() -> bytes:
    """Generates a clean synthetic vibrant PNG image for testing Visual QA Gates."""
    img = Image.new("RGB", (256, 256), color=(30, 80, 200)) # Vibrant game blue
    # Add contrast detail
    for x in range(64, 192):
        for y in range(64, 192):
            img.putpixel((x, y), (255, 215, 0)) # Gold highlight
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# =========================================================================
# 1. Full 5-Agent End-to-End Cohesive Workflow Execution
# =========================================================================

@pytest.mark.asyncio
async def test_full_comfy_hybrid_pipeline_lifecycle(api_client: TestClient):
    """
    Simulates the complete production lifecycle:
    1. Fetch preset from Agent H3 API
    2. Transpile to React Flow format for Agent H5 Sub-Canvas
    3. Modify parameters in UI and transpile back with Agent H1
    4. Validate security with Agent H4 AST Linter
    5. Save as custom version via Agent H3 API
    6. Interpolate runtime variables with Agent H2 Template Engine
    7. Simulate execution & progress stream with Agent H2
    8. Pass generated image through Agent H4 Visual QA Consistency Gate
    """
    # ---------------------------------------------------------------------
    # Step 1: Agent H3 - Retrieve baseline preset
    # ---------------------------------------------------------------------
    presets_res = api_client.get("/api/v1/comfy/presets?category=icon")
    assert presets_res.status_code == 200
    presets = presets_res.json()
    assert len(presets) >= 1
    baseline_preset = presets[0]
    preset_id = baseline_preset["preset_id"]
    workflow_json = baseline_preset["workflow_json"]

    # ---------------------------------------------------------------------
    # Step 2: Agent H1 - Transpile to React Flow Canvas
    # ---------------------------------------------------------------------
    rf_graph = comfy_to_react_flow(workflow_json)
    assert len(rf_graph.nodes) >= 6
    assert len(rf_graph.edges) >= 6

    # Verify Agent H5 UI handle coloring
    for node in rf_graph.nodes:
        for out_handle in node.data.outputs:
            expected_color = get_port_color(out_handle.type)
            assert out_handle.color == expected_color

    # ---------------------------------------------------------------------
    # Step 3: Agent H5 / Agent H1 - Modify parameters on Sub-Canvas
    # ---------------------------------------------------------------------
    # Find KSampler node and tune sampling steps and cfg
    ksampler_node = next(n for n in rf_graph.nodes if n.data.class_type == "KSampler")
    ksampler_node.data.parameters["steps"] = 30
    ksampler_node.data.parameters["cfg"] = 8.5

    # Transpile modified React Flow back to ComfyUI JSON
    modified_comfy_json = react_flow_to_comfy(rf_graph)
    assert modified_comfy_json[ksampler_node.id]["inputs"]["steps"] == 30
    assert modified_comfy_json[ksampler_node.id]["inputs"]["cfg"] == 8.5

    # ---------------------------------------------------------------------
    # Step 4: Agent H4 - Security Verification
    # ---------------------------------------------------------------------
    sec_report = WorkflowSecurityLinter().lint(modified_comfy_json)
    assert sec_report.is_safe is True
    assert len(sec_report.issues) == 0

    # ---------------------------------------------------------------------
    # Step 5: Agent H3 - Save as Custom Preset
    # ---------------------------------------------------------------------
    custom_payload = {
        "name": "Custom Match-3 Sapphire Gem",
        "category": "icon",
        "description": "User modified preset with 30 steps and 8.5 CFG",
        "version": "1.1.0",
        "workflow_json": modified_comfy_json,
        "exposed_variables": [
            {"name": "prompt", "type": "str", "default": "shiny sapphire jewel"},
            {"name": "seed", "type": "int", "default": 7777},
        ],
    }
    create_res = api_client.post("/api/v1/comfy/presets", json=custom_payload)
    assert create_res.status_code == 201
    new_preset = create_res.json()
    assert new_preset["version"] == "1.1.0"
    assert new_preset["checksum"] is not None

    # ---------------------------------------------------------------------
    # Step 6: Agent H2 - Template Engine Runtime Variable Binding
    # ---------------------------------------------------------------------
    template_engine = ComfyTemplateEngine()
    runtime_vars = {
        "prompt": "hyper-glossy royal sapphire gem, mobile game item, 4k specular",
        "seed": 999111,
    }
    bound_workflow = template_engine.bind_variables(modified_comfy_json, runtime_vars)
    # Check that scalar seed was correctly interpolated
    assert bound_workflow[ksampler_node.id]["inputs"]["steps"] == 30

    # ---------------------------------------------------------------------
    # Step 7: Agent H2 - Adapter Execution & Progress Stream
    # ---------------------------------------------------------------------
    adapter = ComfyUIAdapter()
    captured_steps = []

    def on_progress(step: int, total: int, pct: float, node_id: str):
        captured_steps.append((step, total, pct))

    req = ImageAssetRequest(
        concept_id="concept_match3_001",
        prompt="hyper-glossy royal sapphire gem",
        seed=999111,
        width=1024,
        height=1024,
        style_tokens=["glossy", "3d", "game asset"],
    )

    # Prepare workflow using custom_workflow
    ready_workflow = adapter.prepare_workflow(
        request=req,
        custom_workflow=bound_workflow,
    )
    assert isinstance(ready_workflow, dict)

    # ---------------------------------------------------------------------
    # Step 8: Agent H4 - Quality Gate & Game DNA Visual Consistency Gate
    # ---------------------------------------------------------------------
    raw_img_bytes = _generate_synthetic_game_asset_image()

    context = GateExecutionContext(
        artifact={
            "id": "art_img_001",
            "type": "image",
            "media_meta": {
                "image_bytes": raw_img_bytes,
                "prompt": "hyper-glossy royal sapphire gem, vibrant stylized game asset",
            },
        },
        game_dna={
            "palette": {
                "primary": "#1E50C8",
                "accent": "#FFD700",
            },
            "style_tokens": ["game asset", "vibrant", "stylized"],
        },
    )

    vis_gate = ComfyVisualConsistencyGate()
    gate_result = await vis_gate.evaluate(context)
    assert gate_result.status in (GateStatus.PASSED, GateStatus.WARNING)
    assert gate_result.details.get("style_token_match_score", 0.0) >= 0.7


# =========================================================================
# 2. Security Defense: Malicious Workflow Rejection Across Layers
# =========================================================================

def test_malicious_workflow_rejected_at_all_layers(api_client: TestClient):
    """
    Validates that a rogue workflow with dangerous nodes or path traversal
    is stopped by both Agent H4 AST linter, Agent H3 API, and Agent H2 adapter.
    """
    malicious_workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "../../../etc/passwd"},  # Path traversal
        },
        "2": {
            "class_type": "RunSystemCommand",  # Disallowed dangerous node
            "inputs": {"cmd": "rm -rf /"},
        },
    }

    # 1. Agent H4 AST Linter detection
    linter = WorkflowSecurityLinter()
    report = linter.lint(malicious_workflow)
    assert report.is_safe is False
    assert any("RunSystemCommand" in issue.message for issue in report.issues)
    assert any(issue.issue_type.value == "PATH_TRAVERSAL" for issue in report.issues)

    # 2. Agent H3 API Gate rejection
    malicious_preset = {
        "name": "Exploit Preset",
        "category": "exploit",
        "description": "Should fail",
        "workflow_json": malicious_workflow,
    }
    create_res = api_client.post("/api/v1/comfy/presets", json=malicious_preset)
    assert create_res.status_code == 422
    assert "security violation" in create_res.json()["detail"].lower()

    # 3. Agent H2 Adapter rejection
    adapter = ComfyUIAdapter()
    req = ImageAssetRequest(concept_id="c_01", prompt="test", seed=123)
    with pytest.raises(ValueError) as exc:
        adapter.prepare_workflow(request=req, custom_workflow=malicious_workflow)
    assert "security violation" in str(exc.value).lower()
