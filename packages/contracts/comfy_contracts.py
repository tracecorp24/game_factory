"""
Pydantic v2 data contracts for ComfyUI Deep Hybrid Integration.
CreativeForge Intelligence Studio v3.0 - Agent H3.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from pydantic import Field, field_validator

from packages.contracts.common import (
    BaseContractModel,
    compute_sha256,
    generate_uuid,
    utc_now,
)

ComfyModelType = Literal["checkpoint", "lora", "controlnet", "vae", "upscaler"]
ComfyCategoryType = Literal["icon", "character", "background", "layout", "animation", "custom"]


class ComfyVariableSpec(BaseContractModel):
    """Specification of an exposed parameter in a ComfyUI workflow template."""
    name: str = Field(..., description="Variable token name (e.g. 'prompt', 'seed', 'cfg')")
    type: Literal["str", "int", "float", "bool", "combo"] = Field(
        ..., description="Data type for frontend input widget rendering"
    )
    default: Any = Field(..., description="Default fallback value")
    description: Optional[str] = Field(None, description="Human readable description")
    min_val: Optional[float] = Field(None, description="Minimum numeric limit if applicable")
    max_val: Optional[float] = Field(None, description="Maximum numeric limit if applicable")
    options: Optional[List[str]] = Field(None, description="Selection options for combo/dropdown type")


class ComfyModelCatalogItem(BaseContractModel):
    """Catalog item representing a diffusion model / weight file on disk or storage."""
    model_id: str = Field(default_factory=generate_uuid, description="Unique model identifier")
    filename: str = Field(..., description="Filename on disk (e.g. 'dreamshaperXL_v21.safetensors')")
    model_type: ComfyModelType = Field(..., description="Model classification type")
    sha256: str = Field(..., description="Cryptographic SHA256 hash of the weight file")
    size_bytes: int = Field(default=0, ge=0, description="Size of weight file in bytes")
    vram_requirement_mb: int = Field(default=0, ge=0, description="Estimated VRAM allocation requirement in MB")
    is_downloaded: bool = Field(default=True, description="True if local copy exists in models directory")
    local_path: Optional[str] = Field(None, description="Absolute or relative path on local filesystem")
    created_at: datetime = Field(default_factory=utc_now)


class ComfyExecutionProgressEvent(BaseContractModel):
    """Real-time progress telemetry event emitted during ComfyUI KSampler execution."""
    run_id: str = Field(..., description="CreativeForge Run ID")
    node_id: Optional[str] = Field(None, description="Active executing ComfyUI Node ID")
    step: int = Field(..., ge=0, description="Current sampling step (e.g. 14)")
    total_steps: int = Field(..., ge=1, description="Total sampling steps (e.g. 25)")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Percentage of execution completion (0-100)")
    preview_base64: Optional[str] = Field(None, description="Base64 encoded intermediate latent preview JPEG/PNG")


def validate_comfy_workflow_json(workflow: Any) -> Tuple[bool, Optional[str]]:
    """
    Validates that a dictionary conforms to the standard ComfyUI API JSON contract:
    {
        "<node_id>": {
            "class_type": "...",
            "inputs": { ... }
        }
    }
    """
    if not isinstance(workflow, dict):
        return False, "ComfyUI workflow must be a JSON dictionary object."

    if not workflow:
        return False, "ComfyUI workflow dictionary cannot be empty."

    # Direct ComfyUI API format check
    for node_id, node_data in workflow.items():
        if not isinstance(node_data, dict):
            return False, f"Node '{node_id}' definition must be a dictionary object."
        if "class_type" not in node_data:
            return False, f"Node '{node_id}' is missing mandatory 'class_type' attribute."
        if not isinstance(node_data.get("class_type"), str) or not node_data["class_type"].strip():
            return False, f"Node '{node_id}' 'class_type' must be a non-empty string."
        if "inputs" not in node_data:
            return False, f"Node '{node_id}' is missing mandatory 'inputs' dictionary."
        if not isinstance(node_data["inputs"], dict):
            return False, f"Node '{node_id}' 'inputs' must be a dictionary object."

    return True, None


class ComfyPresetRecord(BaseContractModel):
    """Record representing a registered ComfyUI workflow preset with active version and exposed variables."""
    preset_id: str = Field(default_factory=generate_uuid, description="Unique preset identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Preset display title")
    category: str = Field(..., description="Preset category (icon, character, background, layout, custom)")
    description: str = Field(default="", max_length=1024, description="Detailed explanation of the workflow")
    is_builtin: bool = Field(default=False, description="True if shipped as an immutable factory baseline")
    version: str = Field(default="1.0.0", description="Semantic version string")
    workflow_json: Dict[str, Any] = Field(..., description="Raw ComfyUI API JSON graph")
    exposed_variables: List[ComfyVariableSpec] = Field(
        default_factory=list, description="List of dynamic inputs exposed to Studio UI"
    )
    checksum: Optional[str] = Field(None, description="SHA256 checksum of workflow_json")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    @field_validator("workflow_json")
    @classmethod
    def validate_graph(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        is_valid, err_msg = validate_comfy_workflow_json(v)
        if not is_valid:
            raise ValueError(err_msg)
        return v


class ComfyPresetCreate(BaseContractModel):
    """Payload for registering or uploading a new ComfyUI Preset."""
    name: str = Field(..., min_length=2, max_length=255)
    category: str = Field(default="custom", max_length=64)
    description: str = Field(default="", max_length=1024)
    is_builtin: bool = Field(default=False)
    version: str = Field(default="1.0.0")
    workflow_json: Dict[str, Any] = Field(...)
    exposed_variables: List[ComfyVariableSpec] = Field(default_factory=list)

    @field_validator("workflow_json")
    @classmethod
    def validate_graph(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        is_valid, err_msg = validate_comfy_workflow_json(v)
        if not is_valid:
            raise ValueError(err_msg)
        return v


class ComfyPresetUpdate(BaseContractModel):
    """Payload for updating an existing preset metadata or version."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    category: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    workflow_json: Optional[Dict[str, Any]] = None
    exposed_variables: Optional[List[ComfyVariableSpec]] = None

    @field_validator("workflow_json")
    @classmethod
    def validate_optional_graph(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is not None:
            is_valid, err_msg = validate_comfy_workflow_json(v)
            if not is_valid:
                raise ValueError(err_msg)
        return v


class ComfyTestRunRequest(BaseContractModel):
    """Request payload for triggering an interactive or dry-run test render of a preset."""
    variables: Dict[str, Any] = Field(default_factory=dict, description="Values for exposed variables")
    dry_run: bool = Field(default=True, description="If true, verifies and binds variables without dispatching to GPU")


class ComfyTestRunResponse(BaseContractModel):
    """Response payload for a preset test run execution."""
    run_id: str = Field(default_factory=generate_uuid)
    preset_id: str
    status: str = Field(default="QUEUED_TEST", description="Execution status: BOUND, QUEUED_TEST, EXECUTING, or COMPLETED")
    bound_workflow_json: Dict[str, Any] = Field(..., description="ComfyUI graph with variables bound into node inputs")
    variables_applied: Dict[str, Any] = Field(default_factory=dict)
    message: str = Field(default="Workflow parameters bound successfully")
