"""
ComfyUI Node Introspection, Dynamic Schema Extraction, and Component Factory.

Extracts schemas from ComfyUI's /object_info endpoint or offline definitions,
and maps node signatures to React Flow component definitions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

from .types import (
    ComfyPortType,
    ComfySchemaError,
    NodeSchema,
    get_port_color,
)

# Standard ComfyUI Port Types that represent connection edges rather than scalar widgets
COMFY_CONNECTION_PORT_TYPES: Set[str] = {
    ComfyPortType.MODEL.value,
    ComfyPortType.CLIP.value,
    ComfyPortType.VAE.value,
    ComfyPortType.CONDITIONING.value,
    ComfyPortType.LATENT.value,
    ComfyPortType.IMAGE.value,
    ComfyPortType.MASK.value,
    ComfyPortType.CONTROL_NET.value,
    "STYLE_MODEL",
    "CLIP_VISION",
    "GLIGEN",
    "UPSCALE_MODEL",
}

# Standard built-in schemas for core nodes, allowing full offline operation
BUILTIN_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "CheckpointLoaderSimple": {
        "input": {
            "required": {
                "ckpt_name": [["v1-5-pruned-emaonly.safetensors", "sd_xl_base_1.0.safetensors"]]
            }
        },
        "output": ["MODEL", "CLIP", "VAE"],
        "output_name": ["MODEL", "CLIP", "VAE"],
        "name": "CheckpointLoaderSimple",
        "category": "loaders",
    },
    "CLIPTextEncode": {
        "input": {
            "required": {
                "clip": ["CLIP"],
                "text": ["STRING", {"multiline": True, "dynamicPrompts": True}]
            }
        },
        "output": ["CONDITIONING"],
        "output_name": ["CONDITIONING"],
        "name": "CLIPTextEncode",
        "category": "conditioning",
    },
    "EmptyLatentImage": {
        "input": {
            "required": {
                "width": ["INT", {"default": 512, "min": 16, "max": 16384, "step": 8}],
                "height": ["INT", {"default": 512, "min": 16, "max": 16384, "step": 8}],
                "batch_size": ["INT", {"default": 1, "min": 1, "max": 4096}],
            }
        },
        "output": ["LATENT"],
        "output_name": ["LATENT"],
        "name": "EmptyLatentImage",
        "category": "latent",
    },
    "KSampler": {
        "input": {
            "required": {
                "model": ["MODEL"],
                "seed": ["INT", {"default": 0, "min": 0, "max": 18446744073709551615}],
                "steps": ["INT", {"default": 20, "min": 1, "max": 10000}],
                "cfg": ["FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1}],
                "sampler_name": [["euler", "euler_ancestral", "heun", "dpm_2", "ddim", "uni_pc"]],
                "scheduler": [["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]],
                "positive": ["CONDITIONING"],
                "negative": ["CONDITIONING"],
                "latent_image": ["LATENT"],
                "denoise": ["FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}],
            }
        },
        "output": ["LATENT"],
        "output_name": ["LATENT"],
        "name": "KSampler",
        "category": "sampling",
    },
    "KSamplerAdvanced": {
        "input": {
            "required": {
                "model": ["MODEL"],
                "add_noise": [["enable", "disable"]],
                "noise_seed": ["INT", {"default": 0, "min": 0, "max": 18446744073709551615}],
                "steps": ["INT", {"default": 20, "min": 1, "max": 10000}],
                "cfg": ["FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1}],
                "sampler_name": [["euler", "euler_ancestral", "heun", "dpm_2", "ddim"]],
                "scheduler": [["normal", "karras", "exponential", "sgm_uniform", "simple"]],
                "positive": ["CONDITIONING"],
                "negative": ["CONDITIONING"],
                "latent_image": ["LATENT"],
                "start_at_step": ["INT", {"default": 0, "min": 0, "max": 10000}],
                "end_at_step": ["INT", {"default": 10000, "min": 0, "max": 10000}],
                "return_with_leftover_noise": [["disable", "enable"]],
            }
        },
        "output": ["LATENT"],
        "output_name": ["LATENT"],
        "name": "KSamplerAdvanced",
        "category": "sampling",
    },
    "VAEDecode": {
        "input": {
            "required": {
                "samples": ["LATENT"],
                "vae": ["VAE"],
            }
        },
        "output": ["IMAGE"],
        "output_name": ["IMAGE"],
        "name": "VAEDecode",
        "category": "latent",
    },
    "VAEEncode": {
        "input": {
            "required": {
                "pixels": ["IMAGE"],
                "vae": ["VAE"],
            }
        },
        "output": ["LATENT"],
        "output_name": ["LATENT"],
        "name": "VAEEncode",
        "category": "latent",
    },
    "VAELoader": {
        "input": {
            "required": {
                "vae_name": [["ae.safetensors", "vae-ft-mse-840000-ema-pruned.safetensors"]]
            }
        },
        "output": ["VAE"],
        "output_name": ["VAE"],
        "name": "VAELoader",
        "category": "loaders",
    },
    "SaveImage": {
        "input": {
            "required": {
                "filename_prefix": ["STRING", {"default": "ComfyUI"}],
                "images": ["IMAGE"],
            }
        },
        "output": [],
        "output_name": [],
        "name": "SaveImage",
        "category": "image",
    },
    "LoadImage": {
        "input": {
            "required": {
                "image": ["COMBO", {"default": "example.png"}]
            }
        },
        "output": ["IMAGE", "MASK"],
        "output_name": ["IMAGE", "MASK"],
        "name": "LoadImage",
        "category": "image",
    },
    "LoraLoader": {
        "input": {
            "required": {
                "model": ["MODEL"],
                "clip": ["CLIP"],
                "lora_name": ["COMBO", {"default": "lora.safetensors"}],
                "strength_model": ["FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}],
                "strength_clip": ["FLOAT", {"default": 1.0, "min": -20.0, "max": 20.0, "step": 0.01}],
            }
        },
        "output": ["MODEL", "CLIP"],
        "output_name": ["MODEL", "CLIP"],
        "name": "LoraLoader",
        "category": "loaders",
    },
    "ControlNetLoader": {
        "input": {
            "required": {
                "control_net_name": ["COMBO", {"default": "control_canny.safetensors"}]
            }
        },
        "output": ["CONTROL_NET"],
        "output_name": ["CONTROL_NET"],
        "name": "ControlNetLoader",
        "category": "loaders",
    },
    "ControlNetApply": {
        "input": {
            "required": {
                "conditioning": ["CONDITIONING"],
                "control_net": ["CONTROL_NET"],
                "image": ["IMAGE"],
                "strength": ["FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01}],
            }
        },
        "output": ["CONDITIONING"],
        "output_name": ["CONDITIONING"],
        "name": "ControlNetApply",
        "category": "conditioning",
    },
    "CLIPSetLastLayer": {
        "input": {
            "required": {
                "clip": ["CLIP"],
                "stop_at_clip_layer": ["INT", {"default": -1, "min": -24, "max": -1, "step": 1}],
            }
        },
        "output": ["CLIP"],
        "output_name": ["CLIP"],
        "name": "CLIPSetLastLayer",
        "category": "conditioning",
    },
}


class ComfySchemaExtractor:
    """
    Introspects, parses, and provides access to ComfyUI node schemas.
    
    Can load schemas from built-ins, an object_info dictionary, a JSON file,
    or live via HTTP GET /object_info.
    """

    def __init__(
        self,
        schema_data: Optional[Dict[str, Any]] = None,
        comfy_url: Optional[str] = None,
    ):
        self._schemas: Dict[str, NodeSchema] = {}
        # 1. Seed with builtins
        self.load_from_dict(BUILTIN_SCHEMAS)
        # 2. Overlay user-provided schema data
        if schema_data:
            self.load_from_dict(schema_data)
        # 3. If URL provided, fetch
        if comfy_url:
            self.fetch_from_api(comfy_url)

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """Parses ComfyUI /object_info format into NodeSchema instances."""
        if not isinstance(data, dict):
            raise ComfySchemaError("Schema data must be a dictionary keyed by class_type.")

        for class_type, spec in data.items():
            if not isinstance(spec, dict):
                continue
            input_spec = spec.get("input", {})
            required_inputs = input_spec.get("required", {})
            optional_inputs = input_spec.get("optional", {})
            output_types = list(spec.get("output", []))
            output_names = list(spec.get("output_name", []))
            if not output_names and output_types:
                output_names = list(output_types)

            self._schemas[class_type] = NodeSchema(
                class_type=class_type,
                category=spec.get("category", "general"),
                display_name=spec.get("display_name", spec.get("name", class_type)),
                description=spec.get("description"),
                required_inputs=required_inputs,
                optional_inputs=optional_inputs,
                output_types=output_types,
                output_names=output_names,
            )

    def load_from_json_file(self, file_path: Union[str, Path]) -> None:
        """Loads and parses schema from a local JSON file."""
        p = Path(file_path)
        if not p.is_file():
            raise ComfySchemaError(f"Schema file not found at: {file_path}")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.load_from_dict(data)

    def fetch_from_api(self, comfy_url: str = "http://127.0.0.1:8188", timeout: float = 5.0) -> Dict[str, Any]:
        """Fetches /object_info from a running ComfyUI server instance."""
        endpoint = f"{comfy_url.rstrip('/')}/object_info"
        if httpx is not None:
            try:
                response = httpx.get(endpoint, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                self.load_from_dict(data)
                return data
            except Exception as e:
                raise ComfySchemaError(f"Failed to fetch /object_info from {endpoint}: {e}") from e
        else:
            import urllib.request
            try:
                req = urllib.request.Request(endpoint, headers={"User-Agent": "CreativeForge-H1"})
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                self.load_from_dict(data)
                return data
            except Exception as e:
                raise ComfySchemaError(f"Failed to fetch /object_info from {endpoint}: {e}") from e

    def get_node_schema(self, class_type: str) -> Optional[NodeSchema]:
        """Returns the schema for a class_type if known."""
        return self._schemas.get(class_type)

    def list_classes(self) -> List[str]:
        """Returns list of registered class_types."""
        return sorted(list(self._schemas.keys()))

    def get_input_type(self, class_type: str, input_name: str) -> Optional[str]:
        """
        Determines the expected port or widget type for a given node input.
        """
        schema = self.get_node_schema(class_type)
        if not schema:
            return None

        # Check required inputs first
        if input_name in schema.required_inputs:
            spec = schema.required_inputs[input_name]
            return self._extract_type_from_spec(spec)

        # Check optional inputs
        if input_name in schema.optional_inputs:
            spec = schema.optional_inputs[input_name]
            return self._extract_type_from_spec(spec)

        return None

    def get_output_type(self, class_type: str, output_index: int) -> Optional[str]:
        """Returns the type of the output port at output_index."""
        schema = self.get_node_schema(class_type)
        if not schema or output_index < 0 or output_index >= len(schema.output_types):
            return None
        return schema.output_types[output_index]

    def get_output_name(self, class_type: str, output_index: int) -> Optional[str]:
        """Returns the name of the output port at output_index."""
        schema = self.get_node_schema(class_type)
        if not schema:
            return None
        if output_index < len(schema.output_names):
            return schema.output_names[output_index]
        if output_index < len(schema.output_types):
            return schema.output_types[output_index]
        return None

    def is_input_connection_port(self, class_type: str, input_name: str) -> bool:
        """Returns True if the input expects a connection link (e.g. MODEL, LATENT)."""
        input_type = self.get_input_type(class_type, input_name)
        if not input_type:
            return False
        return input_type in COMFY_CONNECTION_PORT_TYPES or input_type in [t.value for t in ComfyPortType]

    def is_input_required(self, class_type: str, input_name: str) -> bool:
        """Returns True if input is in required_inputs."""
        schema = self.get_node_schema(class_type)
        if not schema:
            return False
        return input_name in schema.required_inputs

    def get_required_connection_inputs(self, class_type: str) -> List[Tuple[str, str]]:
        """
        Returns list of (input_name, expected_type) for required connection ports.
        (Widgets with default scalar values like INT/STRING are excluded).
        """
        schema = self.get_node_schema(class_type)
        if not schema:
            return []

        required_conns: List[Tuple[str, str]] = []
        for name, spec in schema.required_inputs.items():
            input_type = self._extract_type_from_spec(spec)
            if input_type in COMFY_CONNECTION_PORT_TYPES:
                required_conns.append((name, input_type))
        return required_conns

    def to_react_flow_definition(self, class_type: str) -> Optional[Dict[str, Any]]:
        """
        Converts a ComfyUI node schema into a React Flow UI component specification.
        """
        schema = self.get_node_schema(class_type)
        if not schema:
            return None

        inputs = []
        # Required inputs
        for name, spec in schema.required_inputs.items():
            inp_type = self._extract_type_from_spec(spec)
            is_conn = inp_type in COMFY_CONNECTION_PORT_TYPES
            inputs.append({
                "id": f"input_{name}",
                "name": name,
                "type": inp_type,
                "color": get_port_color(inp_type),
                "required": True,
                "is_connection": is_conn,
                "default": self._extract_default_from_spec(spec),
            })
        # Optional inputs
        for name, spec in schema.optional_inputs.items():
            inp_type = self._extract_type_from_spec(spec)
            is_conn = inp_type in COMFY_CONNECTION_PORT_TYPES
            inputs.append({
                "id": f"input_{name}",
                "name": name,
                "type": inp_type,
                "color": get_port_color(inp_type),
                "required": False,
                "is_connection": is_conn,
                "default": self._extract_default_from_spec(spec),
            })

        outputs = []
        for idx, out_type in enumerate(schema.output_types):
            out_name = schema.output_names[idx] if idx < len(schema.output_names) else out_type
            outputs.append({
                "id": f"output_{idx}",
                "name": out_name,
                "type": out_type,
                "color": get_port_color(out_type),
                "output_index": idx,
            })

        return {
            "class_type": class_type,
            "display_name": schema.display_name or class_type,
            "category": schema.category,
            "description": schema.description,
            "inputs": inputs,
            "outputs": outputs,
        }

    def _extract_type_from_spec(self, spec: Any) -> str:
        """Ayrıştır: ['MODEL'], ['INT', {...}], or [['opt1', 'opt2']]"""
        if isinstance(spec, list) and spec:
            first = spec[0]
            if isinstance(first, str):
                return first.upper()
            if isinstance(first, list):
                return ComfyPortType.COMBO.value
        elif isinstance(spec, str):
            return spec.upper()
        return ComfyPortType.ANY.value

    def _extract_default_from_spec(self, spec: Any) -> Any:
        if isinstance(spec, list) and len(spec) > 1 and isinstance(spec[1], dict):
            return spec[1].get("default")
        if isinstance(spec, list) and spec and isinstance(spec[0], list) and spec[0]:
            return spec[0][0]
        return None
