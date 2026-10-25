"""
Comprehensive Test Suite for ComfyUI Hybrid Integration:
Data Contracts, Database Models, Atomic Transactions, and REST API Endpoints.
CreativeForge Intelligence Studio v3.0 - Agent H3.
"""
from pathlib import Path
import pytest
from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

from packages.contracts.common import compute_sha256, generate_uuid
from packages.contracts.comfy_contracts import (
    ComfyExecutionProgressEvent,
    ComfyModelCatalogItem,
    ComfyPresetCreate,
    ComfyPresetRecord,
    ComfyTestRunRequest,
    ComfyVariableSpec,
    validate_comfy_workflow_json,
)
from services.api.app.db.base import Base
from services.api.app.db.models.comfy import (
    ComfyModelCatalog,
    ComfyPreset,
    ComfyPresetVersion,
)
from services.api.app.db.session import get_db_session
from services.api.app.main import app
from services.api.app.modules.comfy.service import (
    ComfyNotFoundError,
    ComfyService,
    ComfyValidationError,
    comfy_service,
)

# -----------------------------------------------------------------------------
# 1. DATA CONTRACTS & VALIDATOR TESTS
# -----------------------------------------------------------------------------

def test_comfy_variable_spec_validation():
    var = ComfyVariableSpec(
        name="steps",
        type="int",
        default=25,
        description="Sampling steps",
        min_val=10,
        max_val=50,
    )
    assert var.name == "steps"
    assert var.type == "int"
    assert var.default == 25
    assert var.min_val == 10
    assert var.max_val == 50


def test_comfy_workflow_json_validator():
    # Valid ComfyUI workflow JSON
    valid_wf = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 42,
                "steps": 20,
                "cfg": 7.0,
            },
        }
    }
    is_valid, err = validate_comfy_workflow_json(valid_wf)
    assert is_valid is True
    assert err is None

    # Empty workflow
    is_valid, err = validate_comfy_workflow_json({})
    assert is_valid is False
    assert "empty" in err.lower()

    # Non-dict workflow
    is_valid, err = validate_comfy_workflow_json(["not", "a", "dict"])
    assert is_valid is False

    # Node missing class_type
    invalid_node = {
        "1": {
            "inputs": {"seed": 42}
        }
    }
    is_valid, err = validate_comfy_workflow_json(invalid_node)
    assert is_valid is False
    assert "class_type" in err

    # Node missing inputs
    invalid_inputs = {
        "1": {
            "class_type": "CheckpointLoaderSimple"
        }
    }
    is_valid, err = validate_comfy_workflow_json(invalid_inputs)
    assert is_valid is False
    assert "inputs" in err


def test_comfy_execution_progress_event():
    evt = ComfyExecutionProgressEvent(
        run_id="run_123456",
        node_id="5",
        step=14,
        total_steps=25,
        percentage=56.0,
        preview_base64="data:image/png;base64,iVBORw0KGgo...",
    )
    assert evt.run_id == "run_123456"
    assert evt.node_id == "5"
    assert evt.percentage == 56.0


# -----------------------------------------------------------------------------
# 2. DATABASE MODELS & ATOMIC TRANSACTIONS TESTS
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_comfy_db_models_and_atomic_transactions():
    """
    Validates SQLAlchemy 2.0 schema creation, table registration, and
    atomic insertion of ComfyPreset and ComfyPresetVersion.
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Inspect tables
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda sync_conn: inspect(sync_conn).get_table_names())
        assert "comfy_presets" in tables
        assert "comfy_preset_versions" in tables
        assert "comfy_models" in tables

    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    # Test atomic creation of Preset + Version
    async with async_session() as session:
        preset_id = generate_uuid()
        wf = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
            }
        }
        db_preset = ComfyPreset(
            id=preset_id,
            name="Test Neon Icons",
            category="icon",
            description="Unit test preset",
            is_builtin=False,
            active_version="1.0.0",
        )
        session.add(db_preset)
        await session.flush()

        db_version = ComfyPresetVersion(
            id=generate_uuid(),
            preset_id=preset_id,
            version="1.0.0",
            workflow_json=wf,
            exposed_variables=[{"name": "prompt", "type": "str", "default": "crystal icon"}],
            checksum=compute_sha256(wf),
        )
        session.add(db_version)
        await session.commit()

    # Query back using relationship
    async with async_session() as session:
        stmt = select(ComfyPreset).where(ComfyPreset.id == preset_id)
        res = await session.execute(stmt)
        p = res.scalar_one()
        assert p.name == "Test Neon Icons"
        assert len(p.versions) == 1
        assert p.versions[0].version == "1.0.0"
        assert p.versions[0].workflow_json["1"]["class_type"] == "CheckpointLoaderSimple"

    # Test ComfyModelCatalog DB table
    async with async_session() as session:
        model = ComfyModelCatalog(
            id=generate_uuid(),
            filename="flux1-dev.safetensors",
            model_type="checkpoint",
            sha256="sha256:abcd1234abcd",
            is_downloaded=True,
            size_bytes=12000000000,
            vram_requirement_mb=12288,
        )
        session.add(model)
        await session.commit()

        stmt_m = select(ComfyModelCatalog).where(ComfyModelCatalog.filename == "flux1-dev.safetensors")
        res_m = await session.execute(stmt_m)
        fetched_m = res_m.scalar_one()
        assert fetched_m.model_type == "checkpoint"
        assert fetched_m.vram_requirement_mb == 12288

    await engine.dispose()


# -----------------------------------------------------------------------------
# 3. SERVICE LAYER & VARIABLE BINDING TESTS
# -----------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_comfy_service_variable_binding_and_test_run():
    service = ComfyService()
    presets = await service.list_presets(category="icon")
    assert len(presets) >= 1
    match3_preset = presets[0]

    # Perform test run with variable binding
    req = ComfyTestRunRequest(
        variables={
            "prompt": "super rare legendary ruby gem",
            "seed": 99999,
            "cfg": 8.5,
        },
        dry_run=True,
    )
    response = await service.test_run(match3_preset.preset_id, req)
    assert response.preset_id == match3_preset.preset_id
    assert response.status == "BOUND"
    assert response.variables_applied["seed"] == 99999

    # Verify bound JSON has values substituted
    prompt_node = response.bound_workflow_json["3"]
    assert prompt_node["inputs"]["text"] == "super rare legendary ruby gem"
    ksampler_node = response.bound_workflow_json["5"]
    assert ksampler_node["inputs"]["seed"] == 99999
    assert ksampler_node["inputs"]["cfg"] == 8.5


@pytest.mark.asyncio
async def test_comfy_service_model_scanner_classification(tmp_path: Path):
    """
    Validates model directory scanner correctly classifies checkpoints, loras, and controlnets.
    """
    models_dir = tmp_path / "comfy_models"
    checkpoints_dir = models_dir / "checkpoints"
    loras_dir = models_dir / "loras"
    control_dir = models_dir / "controlnet"

    checkpoints_dir.mkdir(parents=True)
    loras_dir.mkdir(parents=True)
    control_dir.mkdir(parents=True)

    # Create dummy weight files
    (checkpoints_dir / "sdxl_animagine_v3.safetensors").write_bytes(b"SDXL_CHECKPOINT_DUMMY_BYTES")
    (loras_dir / "pixel_art_xl.safetensors").write_bytes(b"LORA_DUMMY_BYTES")
    (control_dir / "control_depth_v11.safetensors").write_bytes(b"CONTROLNET_DUMMY_BYTES")

    service = ComfyService()
    scanned = await service.scan_models(scan_dir=str(models_dir))

    filenames = {m.filename: m.model_type for m in scanned}
    assert "sdxl_animagine_v3.safetensors" in filenames
    assert filenames["sdxl_animagine_v3.safetensors"] == "checkpoint"
    assert "pixel_art_xl.safetensors" in filenames
    assert filenames["pixel_art_xl.safetensors"] == "lora"
    assert "control_depth_v11.safetensors" in filenames
    assert filenames["control_depth_v11.safetensors"] == "controlnet"


# -----------------------------------------------------------------------------
# 4. REST API ENDPOINT INTEGRATION TESTS
# -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def api_client():
    # Setup in-memory SQLite async database override for REST tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    import asyncio
    async def init_schema():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_schema())

    async def override_db():
        async with session_maker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db_session] = override_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.pop(get_db_session, None)
    asyncio.run(engine.dispose())


def test_api_list_presets(api_client: TestClient):
    response = api_client.get("/api/v1/comfy/presets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4  # The 4 built-in pipelines

    # Filter by category
    resp_icon = api_client.get("/api/v1/comfy/presets?category=icon")
    assert resp_icon.status_code == 200
    for p in resp_icon.json():
        assert p["category"] == "icon"

    # Filter by builtin
    resp_builtin = api_client.get("/api/v1/comfy/presets?is_builtin=true")
    assert resp_builtin.status_code == 200
    assert len(resp_builtin.json()) >= 4


def test_api_create_preset_success(api_client: TestClient):
    valid_payload = {
        "name": "Custom Spell Effects Pipeline",
        "category": "animation",
        "description": "Particle and magic effects SDXL workflow",
        "is_builtin": False,
        "version": "1.0.0",
        "workflow_json": {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"},
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"clip": ["1", 1], "text": "${spell_prompt}"},
            },
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "seed": 12345,
                },
            },
        },
        "exposed_variables": [
            {
                "name": "spell_prompt",
                "type": "str",
                "default": "golden lightning strike VFX",
                "description": "Magic effect prompt",
            }
        ],
    }

    res = api_client.post("/api/v1/comfy/presets", json=valid_payload)
    assert res.status_code == 201
    created = res.json()
    assert created["name"] == "Custom Spell Effects Pipeline"
    assert created["preset_id"] is not None
    assert created["checksum"] is not None
    assert len(created["exposed_variables"]) == 1

    # Fetch newly created preset detail
    detail_res = api_client.get(f"/api/v1/comfy/presets/{created['preset_id']}")
    assert detail_res.status_code == 200
    assert detail_res.json()["name"] == "Custom Spell Effects Pipeline"


def test_api_create_preset_invalid_json_unprocessable_entity(api_client: TestClient):
    """
    CRITICAL ACCEPTANCE CRITERION:
    When an invalid ComfyUI JSON is submitted, the API must return 422 Unprocessable Entity.
    """
    # Malformed node missing 'class_type'
    invalid_payload = {
        "name": "Broken Workflow Pipeline",
        "category": "custom",
        "workflow_json": {
            "node_bad": {
                "inputs": {"seed": 42}
                # Missing class_type!
            }
        },
        "exposed_variables": [],
    }

    res = api_client.post("/api/v1/comfy/presets", json=invalid_payload)
    assert res.status_code == 422
    data = res.json()
    assert "detail" in data


def test_api_get_preset_not_found(api_client: TestClient):
    res = api_client.get("/api/v1/comfy/presets/non_existent_preset_uuid_999")
    assert res.status_code == 404


def test_api_trigger_preset_test_run(api_client: TestClient):
    # Retrieve first preset ID
    list_res = api_client.get("/api/v1/comfy/presets")
    preset_id = list_res.json()[0]["preset_id"]

    # Trigger test run
    run_req = {
        "variables": {
            "prompt": "emerald diamond tile item, mobile game asset",
            "seed": 8888,
        },
        "dry_run": True,
    }
    run_res = api_client.post(f"/api/v1/comfy/presets/{preset_id}/test-run", json=run_req)
    assert run_res.status_code == 200
    result = run_res.json()
    assert result["preset_id"] == preset_id
    assert "run_id" in result
    assert result["status"] == "BOUND"
    assert result["variables_applied"]["seed"] == 8888


def test_api_list_and_scan_models(api_client: TestClient):
    # 1. List models
    models_res = api_client.get("/api/v1/comfy/models")
    assert models_res.status_code == 200
    models = models_res.json()
    assert len(models) >= 5

    # Filter by model_type
    ckpt_res = api_client.get("/api/v1/comfy/models?model_type=checkpoint")
    assert ckpt_res.status_code == 200
    for m in ckpt_res.json():
        assert m["model_type"] == "checkpoint"

    # 2. Trigger scan
    scan_res = api_client.post("/api/v1/comfy/models/scan")
    assert scan_res.status_code == 200
    scanned_models = scan_res.json()
    assert len(scanned_models) >= len(models)


def test_api_transpile_and_validate_endpoints(api_client: TestClient):
    sample_workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "2": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": "gold crown coin"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["1", 1], "text": "low quality"}},
        "5": {"class_type": "KSampler", "inputs": {"model": ["1", 0], "positive": ["3", 0], "negative": ["4", 0], "latent_image": ["2", 0], "seed": 42, "steps": 20, "cfg": 7.0, "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"filename_prefix": "Test", "images": ["6", 0]}},
    }

    # 1. Transpile Comfy -> React Flow
    res_to_rf = api_client.post("/api/v1/comfy/transpile/to-react-flow", json=sample_workflow)
    assert res_to_rf.status_code == 200
    rf_graph = res_to_rf.json()
    assert "nodes" in rf_graph and "edges" in rf_graph
    assert len(rf_graph["nodes"]) == 7

    # 2. Transpile React Flow -> Comfy
    res_to_comfy = api_client.post("/api/v1/comfy/transpile/to-comfy", json=rf_graph)
    assert res_to_comfy.status_code == 200
    reconstructed = res_to_comfy.json()
    assert set(reconstructed.keys()) == set(sample_workflow.keys())

    # 3. Validate endpoint
    val_res = api_client.post("/api/v1/comfy/validate", json=sample_workflow)
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["is_valid"] is True
    assert val_data["is_safe"] is True
    assert len(val_data["security_violations"]) == 0
