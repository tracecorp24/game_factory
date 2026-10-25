"""
Comprehensive tests for Agent H2: ComfyUI Daemon Supervisor, WebSocket Progress Streaming,
Dynamic Template Engine, and Production Presets.
"""
import base64
import json
import struct
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from packages.contracts.events import EventEnvelope, EventType
from services.worker_image.daemon import ComfyDaemonSupervisor, ComfyDaemonError
from services.worker_image.template_engine import (
    ComfyTemplateEngine,
    TemplateValueError,
    TemplateVariableMissingError,
)
from services.worker_image.ws_client import ComfyWebSocketListener, ComfyWebSocketError
from services.worker_image.adapters.comfyui_adapter import ComfyUIAdapter
from services.worker_image.image_models import ImageAssetRequest
from services.worker_image.image_worker import ImageWorker


# ==========================================
# 1. TEMPLATE ENGINE TESTS
# ==========================================

def test_template_engine_extract_variables():
    engine = ComfyTemplateEngine()
    sample_workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sd_xl_base.safetensors"},
        },
        "2": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": "${width}", "height": "${height}"},
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "A photo of ${prompt}, style: ${style_tokens}"},
        },
    }

    vars_found = engine.extract_variables(sample_workflow)
    assert set(vars_found) == {"width", "height", "prompt", "style_tokens"}


def test_template_engine_bind_and_type_coercion():
    engine = ComfyTemplateEngine()
    sample_workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": "${seed}",
                "steps": "${steps}",
                "cfg": "${cfg}",
                "denoise": "${denoise}",
            },
        },
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "Hero: ${prompt}, tags: ${style_tokens}"},
        },
    }

    variables = {
        "seed": "987654321",
        "steps": "30",
        "cfg": "8.5",
        "denoise": "0.75",
        "prompt": "Cyberpunk Neon Warrior",
        "style_tokens": ["glowing", "unreal engine 5", "hyperrealistic"],
    }

    bound = engine.bind_variables(sample_workflow, variables)

    # Check strict numeric coercion
    assert bound["3"]["inputs"]["seed"] == 987654321
    assert isinstance(bound["3"]["inputs"]["seed"], int)

    assert bound["3"]["inputs"]["steps"] == 30
    assert isinstance(bound["3"]["inputs"]["steps"], int)

    assert bound["3"]["inputs"]["cfg"] == 8.5
    assert isinstance(bound["3"]["inputs"]["cfg"], float)

    assert bound["3"]["inputs"]["denoise"] == 0.75
    assert isinstance(bound["3"]["inputs"]["denoise"], float)

    # Check list join into string
    assert "Cyberpunk Neon Warrior" in bound["5"]["inputs"]["text"]
    assert "glowing, unreal engine 5, hyperrealistic" in bound["5"]["inputs"]["text"]


def test_template_engine_security_numeric_injection_rejected():
    engine = ComfyTemplateEngine()
    sample_workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {"seed": "${seed}"},
        }
    }

    # Injecting non-integer string into integer field must raise TemplateValueError
    with pytest.raises(TemplateValueError):
        engine.bind_variables(sample_workflow, {"seed": "__import__('os').system('calc')"})

    with pytest.raises(TemplateValueError):
        engine.bind_variables(sample_workflow, {"seed": "1234; DROP TABLE users;"})


def test_template_engine_strict_missing_variable():
    engine = ComfyTemplateEngine(strict=True)
    sample_workflow = {
        "1": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": "${custom_width_param}"},
        }
    }

    with pytest.raises(TemplateVariableMissingError):
        engine.bind_variables(sample_workflow, {})


# ==========================================
# 2. 4 PRODUCTION PRESET INTEGRITY TESTS
# ==========================================

@pytest.mark.parametrize("preset_filename", [
    "match3_gem_icons_sdxl.json",
    "game_hero_portrait_flux.json",
    "controlnet_canny_layout.json",
    "ipadapter_gamedna_consistency.json",
])
def test_production_presets_validity_and_binding(preset_filename):
    preset_path = Path(__file__).resolve().parent.parent / "services" / "worker-image" / "presets" / preset_filename
    assert preset_path.exists(), f"Preset {preset_filename} must exist"

    with open(preset_path, "r", encoding="utf-8") as f:
        workflow_data = json.load(f)

    engine = ComfyTemplateEngine()
    # Validate Comfy node schema
    assert engine.validate_template(workflow_data) is True

    # Test binding standard creative variables
    test_vars = {
        "prompt": "Golden Dragon Gem",
        "negative_prompt": "blurry, low quality",
        "seed": 1337,
        "width": 1024,
        "height": 1024,
        "steps": 25,
        "cfg": 7.0,
        "style_tokens": ["shiny", "vector", "game art"],
        "controlnet_strength": 0.8,
        "ipadapter_weight": 0.75,
        "reference_image": "ref_gem.png",
        "reference_dna_image": "hero_dna.png",
    }

    bound = engine.bind_variables(workflow_data, test_vars)
    assert bound is not None

    # Check that required nodes exist
    class_types = [node["class_type"] for node in bound.values()]
    assert "KSampler" in class_types
    assert "CheckpointLoaderSimple" in class_types
    assert "VAEDecode" in class_types
    assert "SaveImage" in class_types


# ==========================================
# 3. DAEMON SUPERVISOR TESTS
# ==========================================

def test_daemon_command_building():
    supervisor = ComfyDaemonSupervisor(
        comfy_dir=Path(__file__).resolve().parent.parent / "ComfyUI",
        host="0.0.0.0",
        port=8188,
        gpu_device=0,
        vram_mode="highvram",
        extra_args=["--preview-method", "auto"],
    )

    cmd = supervisor.build_command()
    assert "--listen" in cmd and "0.0.0.0" in cmd
    assert "--port" in cmd and "8188" in cmd
    assert "--highvram" in cmd
    assert "--cuda-device" in cmd and "0" in cmd
    assert "--preview-method" in cmd and "auto" in cmd


def test_daemon_start_stop_mocked():
    supervisor = ComfyDaemonSupervisor(
        comfy_dir=Path(__file__).resolve().parent.parent / "ComfyUI",
    )

    mock_proc = MagicMock()
    mock_proc.pid = 9999
    mock_proc.poll.return_value = None

    with patch("subprocess.Popen", return_value=mock_proc):
        supervisor.start(wait_for_ready=False)
        assert supervisor.is_running() is True
        assert supervisor.get_status()["pid"] == 9999

    with patch("subprocess.run") as mock_taskkill:
        supervisor.stop()
        assert supervisor.is_running() is False


def test_daemon_health_check_mocked():
    supervisor = ComfyDaemonSupervisor(
        comfy_dir=Path(__file__).resolve().parent.parent / "ComfyUI",
        auto_restart=False,
    )

    # Mock ping responding with 200 OK
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "system": {"os": "nt", "python_version": "3.12.0"},
        "devices": [{"name": "NVIDIA GeForce RTX 4090", "vram_free": 20000000000, "vram_total": 24000000000}],
    }

    with patch.object(supervisor, "is_running", return_value=True):
        with patch("httpx.Client.get", return_value=mock_response):
            health = supervisor.check_health()
            assert health["healthy"] is True
            assert health["is_responsive"] is True
            assert health["system_stats"]["devices"][0]["name"] == "NVIDIA GeForce RTX 4090"


# ==========================================
# 4. WEBSOCKET PROGRESS LISTENER TESTS
# ==========================================

def test_websocket_listener_progress_event_envelope():
    progress_calls = []

    def progress_cb(val, max_val, pct, node_id):
        progress_calls.append((val, max_val, pct, node_id))

    listener = ComfyWebSocketListener(
        base_ws_url="ws://127.0.0.1:8188",
        client_id="test-client-123",
        project_id="proj_1",
        campaign_id="camp_1",
        request_id="req_1",
        run_id="run_1",
        on_progress=progress_cb,
    )

    # Mock KSampler progress message (step 14 of 25)
    progress_msg = json.dumps({
        "type": "progress",
        "data": {
            "value": 14,
            "max": 25,
            "node": "3",
            "prompt_id": "prompt_xyz",
        },
    })

    envelope = listener.handle_message(progress_msg)

    assert envelope.event_type == EventType.COMFY_STEP_PROGRESS
    assert envelope.run_id == "run_1"
    assert envelope.payload_preview["step"] == 14
    assert envelope.payload_preview["total_steps"] == 25
    assert envelope.payload_preview["percentage"] == 56.0
    assert envelope.verify_integrity() is True

    # Check callback invoked
    assert len(progress_calls) == 1
    assert progress_calls[0] == (14, 25, 56.0, "3")


def test_websocket_listener_binary_preview_frame():
    listener = ComfyWebSocketListener(
        base_ws_url="ws://127.0.0.1:8188",
        project_id="proj_1",
        campaign_id="camp_1",
        request_id="req_1",
        run_id="run_1",
    )

    # Construct mock binary frame: 8-byte header (event_type=1, image_type=1 for JPEG) + raw bytes
    header = struct.pack(">II", 1, 1)
    fake_image_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00dummyjpegbytes"
    binary_frame = header + fake_image_bytes

    envelope = listener.handle_message(binary_frame)

    assert envelope.event_type == EventType.COMFY_PREVIEW_FRAME
    assert envelope.payload_preview["image_format"] == "jpeg"
    assert envelope.payload_preview["bytes_length"] == len(fake_image_bytes)
    assert envelope.verify_integrity() is True


def test_websocket_listener_execution_error():
    listener = ComfyWebSocketListener(
        base_ws_url="ws://127.0.0.1:8188",
        project_id="proj_1",
        campaign_id="camp_1",
        request_id="req_1",
        run_id="run_1",
    )

    error_msg = json.dumps({
        "type": "execution_error",
        "data": {
            "prompt_id": "prompt_fail",
            "node_id": "3",
            "node_type": "KSampler",
            "exception_message": "CUDA out of memory",
            "traceback": ["Traceback...", "OutOfMemoryError"],
        },
    })

    envelope = listener.handle_message(error_msg)

    assert envelope.event_type == EventType.NODE_FAILED
    assert envelope.payload_preview["exception_message"] == "CUDA out of memory"
    assert envelope.payload_preview["node_type"] == "KSampler"
    assert envelope.verify_integrity() is True


# ==========================================
# 5. ADAPTER & WORKER INTEGRATION TESTS
# ==========================================

def test_comfyui_adapter_preset_loading():
    adapter = ComfyUIAdapter(base_url="http://127.0.0.1:8188")
    presets = adapter.list_available_presets()
    assert "match3_gem_icons_sdxl" in presets
    assert "game_hero_portrait_flux" in presets
    assert "controlnet_canny_layout" in presets
    assert "ipadapter_gamedna_consistency" in presets

    loaded = adapter.load_preset("match3_gem_icons_sdxl")
    assert isinstance(loaded, dict)
    assert "5" in loaded


def test_comfyui_adapter_generation_mocked():
    adapter = ComfyUIAdapter(base_url="http://127.0.0.1:8188", timeout_seconds=5.0)

    request = ImageAssetRequest(
        concept_id="test_gem_01",
        prompt="A glittering ruby gem",
        width=512,
        height=512,
        seed=42,
    )

    mock_prompt_resp = MagicMock()
    mock_prompt_resp.status_code = 200
    mock_prompt_resp.json.return_value = {"prompt_id": "mock_pid_123"}

    mock_history_resp = MagicMock()
    mock_history_resp.status_code = 200
    mock_history_resp.json.return_value = {
        "mock_pid_123": {
            "outputs": {
                "7": {"images": [{"filename": "ruby_gem.png", "subfolder": "", "type": "output"}]}
            }
        }
    }

    # Small 1x1 valid PNG bytes
    tiny_png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    mock_view_resp = MagicMock()
    mock_view_resp.status_code = 200
    mock_view_resp.content = tiny_png

    with patch("httpx.Client.post", return_value=mock_prompt_resp):
        with patch("httpx.Client.get", side_effect=[mock_history_resp, mock_view_resp]):
            raw_bytes, meta = adapter.generate(
                request=request,
                preset_name="match3_gem_icons_sdxl",
            )

            assert raw_bytes == tiny_png
            assert meta["comfyui_prompt_id"] == "mock_pid_123"
            assert meta["preset_used"] == "match3_gem_icons_sdxl"
            assert meta["filename"] == "ruby_gem.png"


def test_image_worker_preset_flow_and_fallback():
    worker = ImageWorker(comfyui_url="http://127.0.0.1:8188")

    request = ImageAssetRequest(
        concept_id="test_hero_01",
        prompt="Cyberpunk heroine portrait",
        provider_preference="comfyui",
    )

    # When ComfyUI fails, ImageWorker must gracefully fall back to mock adapter
    with patch.object(worker.comfyui_adapter, "generate", side_effect=RuntimeError("ComfyUI server down")):
        asset = worker.process_comfy_preset(
            preset_name="game_hero_portrait_flux",
            request=request,
            run_id="run_fallback_test",
        )

        assert asset.provider == "mock_fallback"
        assert asset.run_id == "run_fallback_test"
        assert asset.concept_id == "test_hero_01"
        assert asset.storage_ref.startswith("file://") or asset.storage_ref.startswith("storage://")
