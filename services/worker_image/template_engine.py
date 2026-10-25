"""
ComfyUI Template Engine for Dynamic Variable Interpolation and Type Safety.
Handles token binding (${variable_name}), recursive JSON traversal, and strict type casting.
"""
from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional, Set, Union


class TemplateEngineError(Exception):
    """Base exception for ComfyTemplateEngine errors."""
    pass


class TemplateVariableMissingError(TemplateEngineError):
    """Raised when a required template variable is not provided."""
    pass


class TemplateValueError(TemplateEngineError):
    """Raised when a template variable value fails type validation or security checks."""
    pass


class ComfyTemplateEngine:
    """
    Interpolates dynamic variables in ComfyUI workflow JSON structures.
    Guarantees strict type casting for numeric/boolean parameters to prevent injection.
    """

    # Regex to detect ${variable_name}
    VAR_PATTERN = re.compile(r"\$\{([a-zA-Z0-9_\-]+)\}")

    # Fields that strictly require integer values
    INT_FIELDS = {
        "seed", "steps", "width", "height", "batch_size", 
        "start_at_step", "end_at_step", "stop_at_clip_layer",
        "clip_skip", "upscale_by", "max_tokens", "gpu_device"
    }

    # Fields that strictly require float values
    FLOAT_FIELDS = {
        "cfg", "denoise", "strength", "weight", "ipadapter_weight",
        "controlnet_strength", "lora_strength", "guidance",
        "guidance_scale", "noise_strength", "blend_ratio"
    }

    # Fields that strictly require boolean values
    BOOL_FIELDS = {
        "return_with_leftover_noise", "keep_model_loaded",
        "tile", "seamless"
    }

    def __init__(self, strict: bool = False, default_values: Optional[Dict[str, Any]] = None):
        """
        :param strict: If True, raises TemplateVariableMissingError on missing variables.
        :param default_values: Optional default dictionary of variables.
        """
        self.strict = strict
        self.default_values = default_values or {
            "negative_prompt": "ugly, blurry, distorted, low quality, artifacts, watermark",
            "cfg": 7.5,
            "steps": 25,
            "width": 1024,
            "height": 1024,
            "style_tokens": "",
            "seed": 42,
        }

    def extract_variables(self, template_json: Union[dict, list, Any]) -> List[str]:
        """
        Extracts all unique variable names (${var_name}) present in the template.
        """
        found: Set[str] = set()

        def _scan(val: Any):
            if isinstance(val, str):
                for match in self.VAR_PATTERN.finditer(val):
                    found.add(match.group(1))
            elif isinstance(val, dict):
                for v in val.values():
                    _scan(v)
            elif isinstance(val, list):
                for item in val:
                    _scan(item)

        _scan(template_json)
        return sorted(list(found))

    def validate_template(self, template_json: dict) -> bool:
        """
        Validates that template_json is a valid ComfyUI API graph structure.
        """
        if not isinstance(template_json, dict):
            raise TemplateValueError("Workflow template must be a dictionary.")

        for node_id, node_data in template_json.items():
            if not isinstance(node_data, dict):
                raise TemplateValueError(f"Node {node_id} must be a dictionary.")
            if "class_type" not in node_data:
                raise TemplateValueError(f"Node {node_id} is missing 'class_type'.")
            if "inputs" not in node_data or not isinstance(node_data["inputs"], dict):
                raise TemplateValueError(f"Node {node_id} is missing valid 'inputs' dictionary.")

        return True

    def bind_variables(
        self,
        template_json: dict,
        variables: Dict[str, Any],
        strict: Optional[bool] = None,
    ) -> dict:
        """
        Recursively binds variables into the workflow template.
        Supports both exact token replacement (preserving types like int/float) and
        string interpolation within larger text.
        """
        is_strict = self.strict if strict is None else strict

        # Merge with defaults
        combined_vars: Dict[str, Any] = {**self.default_values, **variables}

        # Normalize list values (e.g. style_tokens) to comma-separated strings if needed for text
        normalized_vars: Dict[str, Any] = {}
        for k, v in combined_vars.items():
            normalized_vars[k] = v

        output_json = copy.deepcopy(template_json)

        return self._traverse_and_bind(output_json, normalized_vars, is_strict, current_key=None)

    def _coerce_type(self, key: Optional[str], value: Any) -> Any:
        """
        Coerces value to proper type based on field name or inherent type.
        Rejects harmful injections into numeric fields.
        """
        if key is None:
            return value

        norm_key = key.lower()

        # Check integer fields
        if norm_key in self.INT_FIELDS:
            try:
                if isinstance(value, str):
                    clean_str = value.strip()
                    # Disallow command injections or suspicious strings in numeric fields
                    if not re.match(r"^-?\d+$", clean_str):
                        raise ValueError(f"Value '{value}' is not a valid integer")
                    return int(clean_str)
                elif isinstance(value, (int, float)):
                    return int(value)
                else:
                    raise ValueError(f"Cannot cast {type(value)} to integer")
            except Exception as e:
                raise TemplateValueError(f"Invalid integer value for field '{key}': {value} ({e})") from e

        # Check float fields
        if norm_key in self.FLOAT_FIELDS:
            try:
                if isinstance(value, str):
                    clean_str = value.strip()
                    if not re.match(r"^-?\d+(\.\d+)?$", clean_str):
                        raise ValueError(f"Value '{value}' is not a valid float")
                    return float(clean_str)
                elif isinstance(value, (int, float)):
                    return float(value)
                else:
                    raise ValueError(f"Cannot cast {type(value)} to float")
            except Exception as e:
                raise TemplateValueError(f"Invalid float value for field '{key}': {value} ({e})") from e

        # Check boolean fields
        if norm_key in self.BOOL_FIELDS:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                lower_v = value.strip().lower()
                if lower_v in {"true", "1", "yes"}:
                    return True
                elif lower_v in {"false", "0", "no"}:
                    return False
            raise TemplateValueError(f"Invalid boolean value for field '{key}': {value}")

        return value

    def _traverse_and_bind(
        self,
        node: Any,
        variables: Dict[str, Any],
        strict: bool,
        current_key: Optional[str] = None
    ) -> Any:
        if isinstance(node, dict):
            new_dict = {}
            for k, v in node.items():
                new_dict[k] = self._traverse_and_bind(v, variables, strict, current_key=k)
            return new_dict

        elif isinstance(node, list):
            return [self._traverse_and_bind(elem, variables, strict, current_key=current_key) for elem in node]

        elif isinstance(node, str):
            # Check for exact single variable match: e.g. "${seed}" or "${steps}"
            exact_match = re.fullmatch(r"\$\{([a-zA-Z0-9_\-]+)\}", node.strip())
            if exact_match:
                var_name = exact_match.group(1)
                if var_name not in variables:
                    if strict:
                        raise TemplateVariableMissingError(f"Missing required template variable: '${{{var_name}}}'")
                    return node

                raw_val = variables[var_name]
                # If variable is a list and placed in a string node, convert to string
                if isinstance(raw_val, list):
                    raw_val = ", ".join(str(item) for item in raw_val)

                return self._coerce_type(current_key or var_name, raw_val)

            # Check for multiple or embedded variable matches: e.g. "photo of ${prompt}, ${style_tokens}"
            matches = list(self.VAR_PATTERN.finditer(node))
            if not matches:
                return self._coerce_type(current_key, node)

            result_str = node
            for m in matches:
                var_name = m.group(1)
                token = m.group(0)
                if var_name not in variables:
                    if strict:
                        raise TemplateVariableMissingError(f"Missing required template variable: '${{{var_name}}}'")
                    continue

                val = variables[var_name]
                if isinstance(val, list):
                    val_str = ", ".join(str(item) for item in val)
                else:
                    val_str = str(val)
                result_str = result_str.replace(token, val_str)

            return self._coerce_type(current_key, result_str)

        else:
            return self._coerce_type(current_key, node)
