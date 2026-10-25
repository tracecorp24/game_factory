"""
ComfyUI Hybrid Integration REST API Endpoints.
CreativeForge Intelligence Studio v3.0 - Agent H3.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.comfy_contracts import (
    ComfyModelCatalogItem,
    ComfyPresetCreate,
    ComfyPresetRecord,
    ComfyTestRunRequest,
    ComfyTestRunResponse,
)
from services.api.app.db.session import get_db_session
from services.api.app.modules.comfy.service import (
    ComfyNotFoundError,
    ComfyValidationError,
    comfy_service,
)

router = APIRouter(prefix="", tags=["ComfyUI"])
HTTP_422 = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)


@router.get(
    "/presets",
    response_model=List[ComfyPresetRecord],
    summary="List ComfyUI presets",
    description="Retrieve all available ComfyUI pipeline presets with optional category or text search filters.",
)
async def list_presets(
    category: Optional[str] = Query(None, description="Filter presets by category (icon, character, layout, etc.)"),
    is_builtin: Optional[bool] = Query(None, description="Filter presets by factory baseline vs custom"),
    search: Optional[str] = Query(None, description="Search query string matching name or description"),
    session: Optional[AsyncSession] = Depends(get_db_session),
) -> List[ComfyPresetRecord]:
    return await comfy_service.list_presets(
        category=category,
        is_builtin=is_builtin,
        search=search,
        session=session,
    )


@router.post(
    "/presets",
    response_model=ComfyPresetRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Create ComfyUI preset",
    description="Register a new ComfyUI pipeline preset with full AST and node schema validation.",
)
async def create_preset(
    payload: ComfyPresetCreate,
    session: Optional[AsyncSession] = Depends(get_db_session),
) -> ComfyPresetRecord:
    try:
        return await comfy_service.create_preset(payload, session=session)
    except ComfyValidationError as err:
        raise HTTPException(
            status_code=HTTP_422,
            detail=str(err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create ComfyUI preset: {str(exc)}",
        )


@router.get(
    "/presets/{preset_id}",
    response_model=ComfyPresetRecord,
    summary="Get ComfyUI preset detail",
    description="Fetch a specific ComfyUI workflow preset, active version, and exposed variable definitions.",
)
async def get_preset_detail(
    preset_id: str,
    session: Optional[AsyncSession] = Depends(get_db_session),
) -> ComfyPresetRecord:
    preset = await comfy_service.get_preset(preset_id, session=session)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ComfyUI preset '{preset_id}' was not found.",
        )
    return preset


@router.post(
    "/presets/{preset_id}/test-run",
    response_model=ComfyTestRunResponse,
    summary="Trigger preset test run",
    description="Bind runtime parameters and initiate a test execution or dry-run render for a preset.",
)
async def trigger_preset_test_run(
    preset_id: str,
    payload: ComfyTestRunRequest,
    session: Optional[AsyncSession] = Depends(get_db_session),
) -> ComfyTestRunResponse:
    try:
        return await comfy_service.test_run(preset_id, payload, session=session)
    except ComfyNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )
    except ComfyValidationError as err:
        raise HTTPException(
            status_code=HTTP_422,
            detail=str(err),
        )


@router.get(
    "/models",
    response_model=List[ComfyModelCatalogItem],
    summary="List ComfyUI diffusion models",
    description="Retrieve registered checkpoints, LoRAs, ControlNets, VAEs, and Upscalers.",
)
async def list_models(
    model_type: Optional[str] = Query(None, description="Filter models by type: checkpoint, lora, controlnet, vae, upscaler"),
    session: Optional[AsyncSession] = Depends(get_db_session),
) -> List[ComfyModelCatalogItem]:
    return await comfy_service.list_models(model_type=model_type, session=session)


@router.post(
    "/models/scan",
    response_model=List[ComfyModelCatalogItem],
    summary="Scan disk models",
    description="Scan the disk directory for diffusion model weights and update the database catalog.",
)
async def scan_models_directory(
    scan_dir: Optional[str] = Query(None, description="Target directory path to scan (defaults to ComfyUI/models)"),
    session: Optional[AsyncSession] = Depends(get_db_session),
) -> List[ComfyModelCatalogItem]:
    return await comfy_service.scan_models(scan_dir=scan_dir, session=session)


# -------------------------------------------------------------------------
# Transpiler & Validation Endpoints (Bridging Agent H1, H4 & H5)
# -------------------------------------------------------------------------

@router.post(
    "/transpile/to-react-flow",
    summary="Transpile ComfyUI JSON to React Flow Graph",
    description="Converts a standard ComfyUI API JSON workflow into a React Flow visual graph with auto-layout.",
)
async def transpile_to_react_flow(
    payload: dict,
) -> dict:
    try:
        from packages.comfy_bridge import comfy_to_react_flow
        rf_graph = comfy_to_react_flow(payload)
        return rf_graph.model_dump()
    except Exception as exc:
        raise HTTPException(
            status_code=HTTP_422,
            detail=f"Failed to transpile ComfyUI JSON to React Flow: {str(exc)}",
        )


@router.post(
    "/transpile/to-comfy",
    summary="Transpile React Flow Graph to ComfyUI JSON",
    description="Converts a React Flow visual graph into the standard ComfyUI /prompt API specification.",
)
async def transpile_to_comfy(
    payload: dict,
) -> dict:
    try:
        from packages.comfy_bridge import react_flow_to_comfy
        comfy_dict = react_flow_to_comfy(payload, validate_required=False)
        return comfy_dict
    except Exception as exc:
        raise HTTPException(
            status_code=HTTP_422,
            detail=f"Failed to transpile React Flow to ComfyUI JSON: {str(exc)}",
        )


@router.post(
    "/validate",
    summary="Validate ComfyUI Workflow",
    description="Runs AST Security Linters and Graph Port/Cycle verification on a workflow.",
)
async def validate_workflow(
    payload: dict,
) -> dict:
    try:
        from packages.comfy_bridge import comfy_to_react_flow, validate_workflow_graph
        from services.worker_evaluation.security_rules import WorkflowSecurityLinter

        # If React Flow format (has 'nodes' and 'edges'), convert to comfy first or validate directly
        if "nodes" in payload and "edges" in payload:
            graph_res = validate_workflow_graph(payload, check_required=False)
            from packages.comfy_bridge import react_flow_to_comfy
            comfy_json = react_flow_to_comfy(payload, validate_required=False)
        else:
            comfy_json = payload
            rf_graph = comfy_to_react_flow(comfy_json)
            graph_res = validate_workflow_graph(rf_graph, check_required=False)

        sec_report = WorkflowSecurityLinter().lint(comfy_json)

        return {
            "is_valid": graph_res.is_valid and sec_report.is_safe,
            "is_safe": sec_report.is_safe,
            "graph_errors": graph_res.errors,
            "security_violations": [issue.message for issue in sec_report.issues],
            "security_summary": sec_report.summary,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=HTTP_422,
            detail=f"Workflow validation failed: {str(exc)}",
        )
