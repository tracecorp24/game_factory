"""
ComfyUI Production Adapter with Dynamic Template Interpolation,
Real-Time WebSocket Progress Streaming, and Subprocess Lifecycle Support.
"""
from __future__ import annotations

import io
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import httpx

try:
    from ..image_models import ImageAssetRequest
    from .base import BaseImageAdapter
    from ..template_engine import ComfyTemplateEngine
    from ..ws_client import ComfyWebSocketListener
except (ImportError, ValueError):
    from image_models import ImageAssetRequest
    from adapters.base import BaseImageAdapter
    from template_engine import ComfyTemplateEngine
    from ws_client import ComfyWebSocketListener

logger = logging.getLogger("worker_image.comfyui_adapter")


class ComfyUIAdapter(BaseImageAdapter):
    """
    ComfyUI REST & WebSocket API adapter.
    Supports dynamic parameter binding, preset templates, and live telemetry streaming.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8188",
        timeout_seconds: float = 60.0,
        presets_dir: Optional[Union[str, Path]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.template_engine = ComfyTemplateEngine()

        if presets_dir:
            self.presets_dir = Path(presets_dir)
        else:
            self.presets_dir = Path(__file__).resolve().parent.parent / "presets"

    @property
    def ws_url(self) -> str:
        """Derives WebSocket URL from base_url."""
        if self.base_url.startswith("https://"):
            return "wss://" + self.base_url[8:]
        elif self.base_url.startswith("http://"):
            return "ws://" + self.base_url[7:]
        return f"ws://{self.base_url}"

    def list_available_presets(self) -> List[str]:
        """Returns names of all preset templates found in the presets directory."""
        if not self.presets_dir.exists():
            return []
        return sorted([p.stem for p in self.presets_dir.glob("*.json")])

    def load_preset(self, preset_name: str) -> dict:
        """Loads and parses a preset workflow JSON by name."""
        filename = preset_name if preset_name.endswith(".json") else f"{preset_name}.json"
        preset_path = self.presets_dir / filename
        if not preset_path.exists():
            raise FileNotFoundError(f"ComfyUI preset '{preset_name}' not found at {preset_path}")

        with open(preset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def ping(self, timeout_seconds: float = 3.0) -> bool:
        """Checks if the ComfyUI server is reachable and responsive."""
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                res = client.get(f"{self.base_url}/system_stats")
                return res.status_code == 200
        except Exception:
            return False

    def get_system_stats(self, timeout_seconds: float = 5.0) -> Dict[str, Any]:
        """Fetches hardware status and memory utilization from ComfyUI."""
        with httpx.Client(timeout=timeout_seconds) as client:
            res = client.get(f"{self.base_url}/system_stats")
            res.raise_for_status()
            return res.json()

    def _build_default_workflow(self, request: ImageAssetRequest) -> dict:
        """Fallback standard SD 1.5 default workflow."""
        seed = request.seed if request.seed is not None else int(time.time())
        return {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "cfg": 7.5,
                    "denoise": 1.0,
                    "latent_image": ["5", 0],
                    "model": ["4", 0],
                    "negative": ["7", 0],
                    "positive": ["6", 0],
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "seed": seed,
                    "steps": 25,
                },
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "batch_size": 1,
                    "height": request.height,
                    "width": request.width,
                },
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": f"{request.prompt}, {', '.join(request.style_tokens)}",
                },
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": request.negative_prompt or "ugly, blurry, distorted",
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2],
                },
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "CreativeForge_Gen",
                    "images": ["8", 0],
                },
            },
        }

    def prepare_workflow(
        self,
        request: ImageAssetRequest,
        preset_name: Optional[str] = None,
        custom_workflow: Optional[dict] = None,
        custom_variables: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """
        Prepares a ready-to-execute workflow by interpolating variables into a preset or custom workflow.
        """
        if custom_workflow:
            # Verify AST security before binding dynamic variables
            try:
                from services.worker_evaluation.security_rules import WorkflowSecurityLinter
                sec_report = WorkflowSecurityLinter().lint(custom_workflow)
                if not sec_report.is_safe:
                    raise ValueError(f"Workflow security violation: {sec_report.summary}")
            except ImportError:
                pass
            raw_template = custom_workflow
        elif preset_name:
            raw_template = self.load_preset(preset_name)
        else:
            return self._build_default_workflow(request)

        # Prepare variable dictionary
        variables: Dict[str, Any] = {
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt or "",
            "seed": request.seed if request.seed is not None else int(time.time()),
            "width": request.width,
            "height": request.height,
            "steps": 25,
            "cfg": 7.5,
            "style_tokens": request.style_tokens,
            "controlnet_strength": 0.85,
            "ipadapter_weight": 0.8,
            "reference_image": "reference_ad_layout.png",
            "reference_dna_image": "game_dna_hero.png",
        }

        if custom_variables:
            variables.update(custom_variables)

        # Interpolate variables safely
        return self.template_engine.bind_variables(raw_template, variables)

    def generate(
        self,
        request: ImageAssetRequest,
        preset_name: Optional[str] = None,
        custom_workflow: Optional[dict] = None,
        custom_variables: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, int, float, str], None]] = None,
        event_callback: Optional[Callable[[Any], None]] = None,
        client_id: Optional[str] = None,
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Submits prompt to ComfyUI, streams live execution progress via WebSocket,
        and retrieves output image bytes and execution metadata.
        """
        cid = client_id or str(uuid.uuid4())
        workflow = self.prepare_workflow(
            request=request,
            preset_name=preset_name,
            custom_workflow=custom_workflow,
            custom_variables=custom_variables,
        )

        payload = {
            "prompt": workflow,
            "client_id": cid,
        }

        # Initialize WebSocket progress listener
        ws_listener = ComfyWebSocketListener(
            base_ws_url=self.ws_url,
            client_id=cid,
            on_progress=progress_callback,
            on_event=event_callback,
        )

        # Start listening in background if callback is provided
        if progress_callback or event_callback:
            try:
                ws_listener.start_background(timeout_seconds=self.timeout_seconds)
            except Exception as e:
                logger.warning(f"Could not start background WebSocket listener: {e}")

        with httpx.Client(base_url=self.base_url, timeout=self.timeout_seconds) as client:
            prompt_res = client.post("/prompt", json=payload)
            prompt_res.raise_for_status()
            prompt_data = prompt_res.json()
            prompt_id = prompt_data.get("prompt_id")

            if not prompt_id:
                raise RuntimeError(f"ComfyUI did not return a prompt_id: {prompt_data}")

            start_time = time.time()
            image_filename = None
            image_subfolder = ""
            image_type = "output"

            while time.time() - start_time < self.timeout_seconds:
                history_res = client.get(f"/history/{prompt_id}")
                if history_res.status_code == 200:
                    history_data = history_res.json()
                    if prompt_id in history_data:
                        outputs = history_data[prompt_id].get("outputs", {})
                        for node_id, out in outputs.items():
                            images = out.get("images", [])
                            if images:
                                image_filename = images[0].get("filename")
                                image_subfolder = images[0].get("subfolder", "")
                                image_type = images[0].get("type", "output")
                                break
                        if image_filename:
                            break
                time.sleep(1.0)

            if not image_filename:
                raise TimeoutError(
                    f"ComfyUI generation timed out after {self.timeout_seconds}s for prompt {prompt_id}"
                )

            view_params = {
                "filename": image_filename,
                "subfolder": image_subfolder,
                "type": image_type,
            }
            view_res = client.get("/view", params=view_params)
            view_res.raise_for_status()
            image_bytes = view_res.content

            metadata = {
                "adapter": "ComfyUIAdapter",
                "comfyui_prompt_id": prompt_id,
                "client_id": cid,
                "preset_used": preset_name or "default_sd15",
                "filename": image_filename,
                "elapsed_seconds": round(time.time() - start_time, 2),
                "server_url": self.base_url,
                "events_count": len(ws_listener.captured_events),
            }

            return image_bytes, metadata
