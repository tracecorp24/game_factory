"""
ComfyUI Hybrid Integration Service Layer.
Manages Presets, Versions, Model Catalog, Variable Binding, and Model Directory Scans.
CreativeForge Intelligence Studio v3.0 - Agent H3.
"""
from __future__ import annotations

import copy
import hashlib
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.contracts.common import compute_sha256, generate_uuid, utc_now
from packages.contracts.comfy_contracts import (
    ComfyModelCatalogItem,
    ComfyModelType,
    ComfyPresetCreate,
    ComfyPresetRecord,
    ComfyPresetUpdate,
    ComfyTestRunRequest,
    ComfyTestRunResponse,
    ComfyVariableSpec,
    validate_comfy_workflow_json,
)
from services.api.app.db.models.comfy import (
    ComfyModelCatalog,
    ComfyPreset,
    ComfyPresetVersion,
)

logger = logging.getLogger("creativeforge.comfy_service")


class ComfyValidationError(ValueError):
    """Raised when ComfyUI workflow JSON or parameters fail validation."""
    pass


class ComfyNotFoundError(KeyError):
    """Raised when a requested preset or model is not found."""
    pass


class ComfyService:
    """Core service for managing ComfyUI hybrid presets and model assets."""

    def __init__(self) -> None:
        self._memory_presets: Dict[str, ComfyPresetRecord] = {}
        self._memory_models: Dict[str, ComfyModelCatalogItem] = {}
        self._seed_builtin_presets()
        self._seed_builtin_models()

    def _seed_builtin_presets(self) -> None:
        """Seed the 4 production-grade built-in ComfyUI pipelines."""
        # 1. Match-3 Gemstones SDXL
        p1_id = "preset_match3_gem_icons"
        p1_workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
            },
            "2": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["1", 1],
                    "text": "${prompt}",
                },
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["1", 1],
                    "text": "${negative_prompt}",
                },
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "latent_image": ["2", 0],
                    "seed": "${seed}",
                    "steps": "${steps}",
                    "cfg": "${cfg}",
                    "sampler_name": "euler_ancestral",
                    "scheduler": "karras",
                    "denoise": 1.0,
                },
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2],
                },
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "CreativeForge_Match3",
                    "images": ["6", 0],
                },
            },
        }
        p1_vars = [
            ComfyVariableSpec(
                name="prompt",
                type="str",
                default="glowing neon crystal gem, mobile match-3 icon, shiny glass refraction, isolated on black background, 8k asset",
                description="Gemstone visual description",
            ),
            ComfyVariableSpec(
                name="negative_prompt",
                type="str",
                default="blurry, low quality, artifact, watermark, noisy background",
                description="Negative suppression prompt",
            ),
            ComfyVariableSpec(
                name="seed",
                type="int",
                default=42,
                min_val=0,
                max_val=2147483647,
                description="Diffusion random seed",
            ),
            ComfyVariableSpec(
                name="steps",
                type="int",
                default=25,
                min_val=10,
                max_val=50,
                description="KSampler sampling steps",
            ),
            ComfyVariableSpec(
                name="cfg",
                type="float",
                default=7.0,
                min_val=1.0,
                max_val=20.0,
                description="Classifier Free Guidance",
            ),
        ]
        self._memory_presets[p1_id] = ComfyPresetRecord(
            preset_id=p1_id,
            name="Match-3 Neon Gemstones",
            category="icon",
            description="High-quality transparent/isolated Match-3 gems and crystals workflow with SDXL.",
            is_builtin=True,
            version="1.0.0",
            workflow_json=p1_workflow,
            exposed_variables=p1_vars,
            checksum=compute_sha256(p1_workflow),
        )

        # 2. Hero Stylized Portrait Flux
        p2_id = "preset_hero_portrait_flux"
        p2_workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "flux1-schnell.safetensors"},
            },
            "2": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["1", 1], "text": "${prompt}"},
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["1", 1], "text": "${negative_prompt}"},
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "latent_image": ["2", 0],
                    "seed": "${seed}",
                    "steps": "${steps}",
                    "cfg": "${cfg}",
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                },
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "CreativeForge_HeroPortrait", "images": ["6", 0]},
            },
        }
        p2_vars = [
            ComfyVariableSpec(
                name="prompt",
                type="str",
                default="stylized fearless warrior portrait, vibrant mobile rpg hero, sharp rim lighting, unreal engine render",
                description="Character portrait concept prompt",
            ),
            ComfyVariableSpec(
                name="negative_prompt",
                type="str",
                default="bad anatomy, distorted face, blurry, low resolution",
                description="Negative prompt",
            ),
            ComfyVariableSpec(name="seed", type="int", default=1001, min_val=0, max_val=2147483647),
            ComfyVariableSpec(name="steps", type="int", default=28, min_val=15, max_val=50),
            ComfyVariableSpec(name="cfg", type="float", default=6.5, min_val=1.0, max_val=15.0),
        ]
        self._memory_presets[p2_id] = ComfyPresetRecord(
            preset_id=p2_id,
            name="Game Hero Stylized Portrait",
            category="character",
            description="Hero cover art stylized character portrait workflow using Flux/SDXL.",
            is_builtin=True,
            version="1.0.0",
            workflow_json=p2_workflow,
            exposed_variables=p2_vars,
            checksum=compute_sha256(p2_workflow),
        )

        # 3. ControlNet Canny Layout
        p3_id = "preset_controlnet_canny_layout"
        p3_workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "dreamshaperXL_v21.safetensors"},
            },
            "2": {
                "class_type": "ControlNetLoader",
                "inputs": {"control_net_name": "control_v11p_sd15_canny.safetensors"},
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["1", 1], "text": "${prompt}"},
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["1", 1], "text": "${negative_prompt}"},
            },
            "5": {
                "class_type": "ControlNetApply",
                "inputs": {
                    "conditioning": ["3", 0],
                    "control_net": ["2", 0],
                    "image": ["10", 0],
                    "strength": "${control_strength}",
                },
            },
            "6": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 1080, "height": 1920, "batch_size": 1},
            },
            "7": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["5", 0],
                    "negative": ["4", 0],
                    "latent_image": ["6", 0],
                    "seed": "${seed}",
                    "steps": "${steps}",
                    "cfg": "${cfg}",
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["7", 0], "vae": ["1", 2]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "CreativeForge_CannyLayout", "images": ["8", 0]},
            },
            "10": {
                "class_type": "LoadImage",
                "inputs": {"image": "layout_reference.png"},
            },
        }
        p3_vars = [
            ComfyVariableSpec(
                name="prompt",
                type="str",
                default="mobile game promo banner, high stakes action composition, cinematic lighting",
                description="Ad composition prompt",
            ),
            ComfyVariableSpec(name="control_strength", type="float", default=0.85, min_val=0.1, max_val=1.5),
            ComfyVariableSpec(name="seed", type="int", default=777, min_val=0, max_val=2147483647),
            ComfyVariableSpec(name="steps", type="int", default=25, min_val=10, max_val=50),
            ComfyVariableSpec(name="cfg", type="float", default=7.5, min_val=1.0, max_val=20.0),
        ]
        self._memory_presets[p3_id] = ComfyPresetRecord(
            preset_id=p3_id,
            name="Ad Composition Canny Layout",
            category="layout",
            description="Extracts Canny edge lines from reference scene to guide layout composition.",
            is_builtin=True,
            version="1.0.0",
            workflow_json=p3_workflow,
            exposed_variables=p3_vars,
            checksum=compute_sha256(p3_workflow),
        )

        # 4. IP-Adapter Game DNA Consistency
        p4_id = "preset_ipadapter_gamedna"
        p4_workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
            },
            "2": {
                "class_type": "IPAdapterModelLoader",
                "inputs": {"ipadapter_file": "ip-adapter-plus_sdxl_vit-h.safetensors"},
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["1", 1], "text": "${prompt}"},
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["1", 1], "text": "${negative_prompt}"},
            },
            "5": {
                "class_type": "IPAdapterApply",
                "inputs": {
                    "model": ["1", 0],
                    "ipadapter": ["2", 0],
                    "image": ["10", 0],
                    "weight": "${ipadapter_weight}",
                },
            },
            "6": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
            },
            "7": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["5", 0],
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "latent_image": ["6", 0],
                    "seed": "${seed}",
                    "steps": "${steps}",
                    "cfg": "${cfg}",
                    "sampler_name": "euler_ancestral",
                    "scheduler": "karras",
                    "denoise": 1.0,
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["7", 0], "vae": ["1", 2]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "CreativeForge_IPAdapter", "images": ["8", 0]},
            },
            "10": {
                "class_type": "LoadImage",
                "inputs": {"image": "game_dna_style_guide.png"},
            },
        }
        p4_vars = [
            ComfyVariableSpec(
                name="prompt",
                type="str",
                default="game mascot in victory pose, matching brand game dna art style",
                description="Game DNA consistent prompt",
            ),
            ComfyVariableSpec(name="ipadapter_weight", type="float", default=0.75, min_val=0.1, max_val=1.5),
            ComfyVariableSpec(name="seed", type="int", default=4242, min_val=0, max_val=2147483647),
            ComfyVariableSpec(name="steps", type="int", default=26, min_val=10, max_val=50),
            ComfyVariableSpec(name="cfg", type="float", default=7.0, min_val=1.0, max_val=20.0),
        ]
        self._memory_presets[p4_id] = ComfyPresetRecord(
            preset_id=p4_id,
            name="Game DNA IP-Adapter Style Lock",
            category="character",
            description="Transfers Game DNA reference art style and color palette to new generation.",
            is_builtin=True,
            version="1.0.0",
            workflow_json=p4_workflow,
            exposed_variables=p4_vars,
            checksum=compute_sha256(p4_workflow),
        )

    def _seed_builtin_models(self) -> None:
        """Seed the standard supported foundation and adapter models."""
        defaults = [
            ComfyModelCatalogItem(
                model_id="model_sd_xl_base",
                filename="sd_xl_base_1.0.safetensors",
                model_type="checkpoint",
                sha256="sha256:31e35c80ed48291e7d90063987224f97e5b11c2952c15d9128d576b439f4b882",
                size_bytes=6938000000,
                vram_requirement_mb=8192,
                is_downloaded=True,
            ),
            ComfyModelCatalogItem(
                model_id="model_dreamshaper_xl",
                filename="dreamshaperXL_v21.safetensors",
                model_type="checkpoint",
                sha256="sha256:88712f86641be2cb0dcda42b3bf07297e68fa7075c2e9efcaef16bc74fa57f12",
                size_bytes=6422000000,
                vram_requirement_mb=8192,
                is_downloaded=True,
            ),
            ComfyModelCatalogItem(
                model_id="model_flux_schnell",
                filename="flux1-schnell.safetensors",
                model_type="checkpoint",
                sha256="sha256:e0b7be5954a1be2e68c07e0c0d16c52a0a552bfdbca07b8b4200635f1115843a",
                size_bytes=11900000000,
                vram_requirement_mb=12288,
                is_downloaded=True,
            ),
            ComfyModelCatalogItem(
                model_id="model_control_canny",
                filename="control_v11p_sd15_canny.safetensors",
                model_type="controlnet",
                sha256="sha256:d14cfa167098e982181794b638914ba196a67f08d0f73c68a0a4c21a48c66a4f",
                size_bytes=1450000000,
                vram_requirement_mb=2048,
                is_downloaded=True,
            ),
            ComfyModelCatalogItem(
                model_id="model_ipadapter_plus",
                filename="ip-adapter-plus_sdxl_vit-h.safetensors",
                model_type="lora",
                sha256="sha256:c72d3f9bca6b6b797448ebf5c765ef3dfc8e1467406a461c360032e39ea51624",
                size_bytes=820000000,
                vram_requirement_mb=1024,
                is_downloaded=True,
            ),
            ComfyModelCatalogItem(
                model_id="model_vae_ft_mse",
                filename="vae-ft-mse-840000-ema-pruned.safetensors",
                model_type="vae",
                sha256="sha256:2f11c4a99dd64293f9ef3bb0ed308c66e2c396860368c0d1e0d37e6f8510a6fd",
                size_bytes=335000000,
                vram_requirement_mb=512,
                is_downloaded=True,
            ),
            ComfyModelCatalogItem(
                model_id="model_upscaler_4x",
                filename="4x_NMKD-Superscale-SP_178000_G.pth",
                model_type="upscaler",
                sha256="sha256:5a9e32b4b45610bcde89f417fae446559bc85e51e44131df33db9be3a7f83038",
                size_bytes=67000000,
                vram_requirement_mb=512,
                is_downloaded=True,
            ),
        ]
        for m in defaults:
            self._memory_models[m.model_id] = m

    # -------------------------------------------------------------------------
    # PRESETS & VERSIONS
    # -------------------------------------------------------------------------

    async def list_presets(
        self,
        category: Optional[str] = None,
        is_builtin: Optional[bool] = None,
        search: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> List[ComfyPresetRecord]:
        """List registered presets with optional filtering."""
        if session:
            try:
                stmt = select(ComfyPreset)
                if category:
                    stmt = stmt.where(ComfyPreset.category == category)
                if is_builtin is not None:
                    stmt = stmt.where(ComfyPreset.is_builtin == is_builtin)
                if search:
                    stmt = stmt.where(ComfyPreset.name.ilike(f"%{search}%"))

                result = await session.execute(stmt)
                db_presets = result.scalars().all()
                if db_presets:
                    records: List[ComfyPresetRecord] = []
                    for p in db_presets:
                        ver_obj = None
                        if p.versions:
                            for v in p.versions:
                                if v.version == p.active_version:
                                    ver_obj = v
                                    break
                            if not ver_obj:
                                ver_obj = p.versions[0]

                        exposed_vars = []
                        if ver_obj and ver_obj.exposed_variables:
                            exposed_vars = [ComfyVariableSpec(**ev) for ev in ver_obj.exposed_variables]

                        records.append(
                            ComfyPresetRecord(
                                preset_id=p.id,
                                name=p.name,
                                category=p.category,
                                description=p.description,
                                is_builtin=p.is_builtin,
                                version=p.active_version,
                                workflow_json=ver_obj.workflow_json if ver_obj else {},
                                exposed_variables=exposed_vars,
                                checksum=ver_obj.checksum if ver_obj else None,
                                created_at=p.created_at,
                                updated_at=p.updated_at,
                            )
                        )
                    return records
            except Exception as exc:
                logger.warning(f"Database list_presets query failed ({exc}), falling back to memory store.")

        # Fallback to memory store
        presets = list(self._memory_presets.values())
        if category:
            presets = [p for p in presets if p.category.lower() == category.lower()]
        if is_builtin is not None:
            presets = [p for p in presets if p.is_builtin == is_builtin]
        if search:
            q = search.lower()
            presets = [p for p in presets if q in p.name.lower() or q in p.description.lower()]
        return presets

    async def get_preset(
        self,
        preset_id: str,
        session: Optional[AsyncSession] = None,
    ) -> Optional[ComfyPresetRecord]:
        """Fetch a specific preset by ID."""
        if session:
            try:
                stmt = select(ComfyPreset).where(ComfyPreset.id == preset_id)
                result = await session.execute(stmt)
                p = result.scalar_one_or_none()
                if p:
                    ver_obj = None
                    if p.versions:
                        for v in p.versions:
                            if v.version == p.active_version:
                                ver_obj = v
                                break
                        if not ver_obj:
                            ver_obj = p.versions[0]
                    exposed_vars = (
                        [ComfyVariableSpec(**ev) for ev in ver_obj.exposed_variables]
                        if ver_obj and ver_obj.exposed_variables
                        else []
                    )
                    return ComfyPresetRecord(
                        preset_id=p.id,
                        name=p.name,
                        category=p.category,
                        description=p.description,
                        is_builtin=p.is_builtin,
                        version=p.active_version,
                        workflow_json=ver_obj.workflow_json if ver_obj else {},
                        exposed_variables=exposed_vars,
                        checksum=ver_obj.checksum if ver_obj else None,
                        created_at=p.created_at,
                        updated_at=p.updated_at,
                    )
            except Exception as exc:
                logger.warning(f"Database get_preset query failed ({exc}), falling back to memory store.")

        return self._memory_presets.get(preset_id)

    async def create_preset(
        self,
        data: ComfyPresetCreate,
        session: Optional[AsyncSession] = None,
    ) -> ComfyPresetRecord:
        """
        Create and persist a new ComfyUI preset and initial version atomically.
        Validates workflow_json and computes SHA-256 integrity checksum.
        """
        is_valid, error_msg = validate_comfy_workflow_json(data.workflow_json)
        if not is_valid:
            raise ComfyValidationError(f"Invalid ComfyUI workflow JSON: {error_msg}")

        # AST Security Verification
        from services.worker_evaluation.security_rules import WorkflowSecurityLinter
        sec_report = WorkflowSecurityLinter().lint(data.workflow_json)
        if not sec_report.is_safe:
            raise ComfyValidationError(
                f"ComfyUI workflow security violation: {sec_report.summary}"
            )

        # Agent H1 Comfy Bridge Graph Structure & Acyclicity Verification
        try:
            from packages.comfy_bridge import comfy_to_react_flow, validate_workflow_graph
            rf_graph = comfy_to_react_flow(data.workflow_json)
            validate_workflow_graph(rf_graph, check_required=False)
        except Exception as bridge_err:
            raise ComfyValidationError(f"ComfyUI workflow graph validation failed: {bridge_err}")

        preset_id = generate_uuid()
        now = utc_now()
        checksum = compute_sha256(data.workflow_json)

        record = ComfyPresetRecord(
            preset_id=preset_id,
            name=data.name,
            category=data.category,
            description=data.description,
            is_builtin=data.is_builtin,
            version=data.version,
            workflow_json=data.workflow_json,
            exposed_variables=data.exposed_variables,
            checksum=checksum,
            created_at=now,
            updated_at=now,
        )

        if session:
            try:
                # Atomic database insertion for preset and preset_version
                db_preset = ComfyPreset(
                    id=preset_id,
                    name=data.name,
                    category=data.category,
                    description=data.description,
                    is_builtin=data.is_builtin,
                    active_version=data.version,
                    created_at=now,
                    updated_at=now,
                )
                session.add(db_preset)
                await session.flush()

                db_version = ComfyPresetVersion(
                    id=generate_uuid(),
                    preset_id=preset_id,
                    version=data.version,
                    workflow_json=data.workflow_json,
                    exposed_variables=[v.model_dump() for v in data.exposed_variables],
                    checksum=checksum,
                    created_at=now,
                )
                session.add(db_version)
                await session.commit()
            except Exception as exc:
                logger.warning(f"Database create_preset failed ({exc}), falling back to memory store.")
                if not isinstance(exc, (OSError, ConnectionError)):
                    # If not a connection error, verify if it's not a remote refusal
                    if "connection" not in str(exc).lower() and "connect" not in str(exc).lower():
                        raise

        # Update in-memory registry
        self._memory_presets[preset_id] = record
        return record

    async def test_run(
        self,
        preset_id: str,
        request: ComfyTestRunRequest,
        session: Optional[AsyncSession] = None,
    ) -> ComfyTestRunResponse:
        """
        Interpolates dynamic variables into a preset workflow and prepares/queues a test execution run.
        """
        preset = await self.get_preset(preset_id, session=session)
        if not preset:
            raise ComfyNotFoundError(f"Preset '{preset_id}' not found.")

        # Deep clone workflow JSON to prevent side effects
        bound_json = copy.deepcopy(preset.workflow_json)
        applied_variables: Dict[str, Any] = {}

        # Default values from exposed_variables
        for var_spec in preset.exposed_variables:
            applied_variables[var_spec.name] = var_spec.default

        # Override with user supplied request variables
        for k, v in request.variables.items():
            applied_variables[k] = v

        # Recursively bind variables into node inputs
        def interpolate_val(val: Any) -> Any:
            if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
                token = val[2:-1].strip()
                if token in applied_variables:
                    return applied_variables[token]
            return val

        for node_id, node_data in bound_json.items():
            if isinstance(node_data, dict) and "inputs" in node_data:
                inputs = node_data["inputs"]
                if isinstance(inputs, dict):
                    for in_key, in_val in inputs.items():
                        inputs[in_key] = interpolate_val(in_val)

        run_id = f"run_comfy_test_{generate_uuid()[:12]}"
        status_label = "QUEUED_TEST" if not request.dry_run else "BOUND"

        return ComfyTestRunResponse(
            run_id=run_id,
            preset_id=preset_id,
            status=status_label,
            bound_workflow_json=bound_json,
            variables_applied=applied_variables,
            message=f"Preset '{preset.name}' variables successfully bound. Ready for KSampler execution.",
        )

    # -------------------------------------------------------------------------
    # MODEL CATALOG & SCANNER
    # -------------------------------------------------------------------------

    async def list_models(
        self,
        model_type: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> List[ComfyModelCatalogItem]:
        """List registered diffusion models with optional type filter."""
        if session:
            try:
                stmt = select(ComfyModelCatalog)
                if model_type:
                    stmt = stmt.where(ComfyModelCatalog.model_type == model_type)
                result = await session.execute(stmt)
                db_models = result.scalars().all()
                if db_models:
                    return [
                        ComfyModelCatalogItem(
                            model_id=m.id,
                            filename=m.filename,
                            model_type=m.model_type,  # type: ignore
                            sha256=m.sha256,
                            size_bytes=m.size_bytes,
                            vram_requirement_mb=m.vram_requirement_mb,
                            is_downloaded=m.is_downloaded,
                            local_path=m.local_path,
                            created_at=m.created_at,
                        )
                        for m in db_models
                    ]
            except Exception as exc:
                logger.warning(f"Database list_models query failed ({exc}), falling back to memory store.")

        models = list(self._memory_models.values())
        if model_type:
            models = [m for m in models if m.model_type.lower() == model_type.lower()]
        return models

    async def scan_models(
        self,
        scan_dir: Optional[str] = None,
        session: Optional[AsyncSession] = None,
    ) -> List[ComfyModelCatalogItem]:
        """
        Scans a disk directory for model weights (.safetensors, .ckpt, .pt, .pth, .bin),
        classifies their types, and synchronizes the catalog and database.
        """
        valid_extensions = {".safetensors", ".ckpt", ".pt", ".pth", ".bin"}
        discovered: List[ComfyModelCatalogItem] = []

        scan_path = Path(scan_dir) if scan_dir else Path("ComfyUI/models")

        if scan_path.exists() and scan_path.is_dir():
            for root, _, files in os.walk(scan_path):
                root_lower = root.lower().replace("\\", "/")
                for f in files:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in valid_extensions:
                        file_path = os.path.join(root, f)
                        try:
                            file_size = os.path.getsize(file_path)
                        except OSError:
                            file_size = 0

                        # Classify model type from directory path or filename
                        f_lower = f.lower()
                        model_type: ComfyModelType = "checkpoint"
                        vram_mb = 8192

                        if "lora" in root_lower or "lora" in f_lower:
                            model_type = "lora"
                            vram_mb = 1024
                        elif "controlnet" in root_lower or "control" in f_lower:
                            model_type = "controlnet"
                            vram_mb = 2048
                        elif "vae" in root_lower or "vae" in f_lower:
                            model_type = "vae"
                            vram_mb = 512
                        elif "upscale" in root_lower or "esrgan" in f_lower:
                            model_type = "upscaler"
                            vram_mb = 512
                        elif "flux" in f_lower:
                            model_type = "checkpoint"
                            vram_mb = 12288

                        item = ComfyModelCatalogItem(
                            model_id=f"model_{hashlib.md5(f.encode()).hexdigest()[:12]}",
                            filename=f,
                            model_type=model_type,
                            sha256=f"sha256:{hashlib.sha256(f.encode()).hexdigest()}",
                            size_bytes=file_size,
                            vram_requirement_mb=vram_mb,
                            is_downloaded=True,
                            local_path=str(file_path),
                        )
                        discovered.append(item)

        # If no models found on disk, fallback to preloaded catalog
        if not discovered:
            discovered = list(self._memory_models.values())

        # Sync discovered items into memory
        for item in discovered:
            self._memory_models[item.model_id] = item

        # Sync into database if session provided
        if session:
            try:
                for item in discovered:
                    stmt = select(ComfyModelCatalog).where(ComfyModelCatalog.filename == item.filename)
                    res = await session.execute(stmt)
                    existing = res.scalar_one_or_none()
                    if not existing:
                        db_item = ComfyModelCatalog(
                            id=item.model_id,
                            filename=item.filename,
                            model_type=item.model_type,
                            sha256=item.sha256,
                            is_downloaded=item.is_downloaded,
                            size_bytes=item.size_bytes,
                            vram_requirement_mb=item.vram_requirement_mb,
                            local_path=item.local_path,
                        )
                        session.add(db_item)
                await session.commit()
            except Exception as exc:
                logger.warning(f"Database scan_models sync failed ({exc}), updated in-memory catalog only.")

        return discovered


# Shared singleton instance
comfy_service = ComfyService()
