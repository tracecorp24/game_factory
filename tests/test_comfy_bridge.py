"""
Comprehensive Tests for ComfyUI Bridge (Agent H1).

Covers:
1. Port Types & Color Palette standards
2. Schema Introspection & /object_info extraction
3. Bidirectional Transpilation (ComfyUI API JSON <-> React Flow Graph)
4. Sugiyama/DAG Hierarchical Auto-Layout
5. 100% Roundtrip Equivalence on Production Presets
6. Edge Type Checking (ComfyTypeMismatchError)
7. DAG Cycle Detection (ComfyCycleError)
8. Missing Required Port Validation (ComfyMissingPortError)
"""

from pathlib import Path
import json
import pytest

from packages.comfy_bridge.types import (
    ComfyPortType,
    PORT_COLORS,
    DEFAULT_PORT_COLOR,
    get_port_color,
    ComfyBridgeError,
    ComfyTypeMismatchError,
    ComfyCycleError,
    ComfyMissingPortError,
    ComfyValidationError,
    ComfySchemaError,
    ReactFlowGraph,
    ReactFlowNode,
    ReactFlowEdge,
    ReactFlowNodeData,
    Position,
    HandleDefinition,
)
from packages.comfy_bridge.introspection import (
    ComfySchemaExtractor,
    BUILTIN_SCHEMAS,
    COMFY_CONNECTION_PORT_TYPES,
)
from packages.comfy_bridge.transpiler import (
    comfy_to_react_flow,
    react_flow_to_comfy,
)
from packages.comfy_bridge.validator import (
    validate_comfy_edge,
    validate_workflow_graph,
    detect_cycles,
    are_types_compatible,
)

PRESETS_DIR = Path(__file__).resolve().parent.parent / "packages" / "comfy-bridge" / "presets"


# =========================================================================
# 1. Port Types & Color Palette Tests
# =========================================================================

def test_port_type_values_and_colors():
    """Verifies that all specified ComfyUI port types have exact required hex colors."""
    expected_colors = {
        ComfyPortType.MODEL.value: "#b197fc",        # Açık Mor
        ComfyPortType.CLIP.value: "#ffd43b",         # Sarı
        ComfyPortType.VAE.value: "#ff6b6b",          # Kırmızı
        ComfyPortType.CONDITIONING.value: "#ffa94d", # Turuncu
        ComfyPortType.LATENT.value: "#da77f2",       # Mor
        ComfyPortType.IMAGE.value: "#4dabf7",        # Mavi
        ComfyPortType.MASK.value: "#ced4da",         # Gri
        ComfyPortType.CONTROL_NET.value: "#51cf66",  # Yeşil
    }

    for port_type, hex_code in expected_colors.items():
        assert PORT_COLORS[port_type] == hex_code
        assert get_port_color(port_type) == hex_code
        assert get_port_color(port_type.lower()) == hex_code

    # Fallback for unknown type
    assert get_port_color("UNKNOWN_CUSTOM_TYPE") == DEFAULT_PORT_COLOR


# =========================================================================
# 2. Schema Introspection & Extractor Tests
# =========================================================================

def test_schema_extractor_builtins():
    """Verifies that the built-in catalog contains essential ComfyUI node definitions."""
    extractor = ComfySchemaExtractor()
    classes = extractor.list_classes()

    essential_nodes = [
        "CheckpointLoaderSimple",
        "CLIPTextEncode",
        "EmptyLatentImage",
        "KSampler",
        "VAEDecode",
        "SaveImage",
        "ControlNetLoader",
        "ControlNetApply",
    ]
    for node_name in essential_nodes:
        assert node_name in classes, f"Node {node_name} missing from built-in schemas"

    # Test KSampler schema details
    ksampler = extractor.get_node_schema("KSampler")
    assert ksampler is not None
    assert ksampler.output_types == ["LATENT"]

    # KSampler required connection ports
    req_conns = extractor.get_required_connection_inputs("KSampler")
    req_map = dict(req_conns)
    assert req_map.get("model") == "MODEL"
    assert req_map.get("positive") == "CONDITIONING"
    assert req_map.get("negative") == "CONDITIONING"
    assert req_map.get("latent_image") == "LATENT"

    # Scalar parameter input type resolution
    assert extractor.get_input_type("KSampler", "steps") == "INT"
    assert extractor.get_input_type("KSampler", "cfg") == "FLOAT"
    assert extractor.get_input_type("KSampler", "sampler_name") == "COMBO"


def test_schema_extractor_custom_dict_and_react_flow_def():
    """Tests loading dynamic custom nodes and converting schema to React Flow node definition."""
    custom_schema = {
        "CustomUpscaler": {
            "input": {
                "required": {
                    "image": ["IMAGE"],
                    "scale_by": ["FLOAT", {"default": 2.0, "min": 1.0, "max": 8.0, "step": 0.5}],
                },
                "optional": {
                    "mask": ["MASK"],
                }
            },
            "output": ["IMAGE"],
            "output_name": ["IMAGE"],
            "category": "upscaling",
        }
    }
    extractor = ComfySchemaExtractor(schema_data=custom_schema)
    assert "CustomUpscaler" in extractor.list_classes()

    rf_def = extractor.to_react_flow_definition("CustomUpscaler")
    assert rf_def is not None
    assert rf_def["class_type"] == "CustomUpscaler"
    assert rf_def["category"] == "upscaling"
    assert len(rf_def["inputs"]) == 3  # image, scale_by, mask
    assert len(rf_def["outputs"]) == 1  # IMAGE


# =========================================================================
# 3. Transpiler: comfy_to_react_flow Tests
# =========================================================================

def test_comfy_to_react_flow_basic():
    """Tests transpiling standard txt2img workflow into React Flow format."""
    preset_path = PRESETS_DIR / "default_txt2img.json"
    assert preset_path.exists(), "Preset default_txt2img.json not found"

    with open(preset_path, "r", encoding="utf-8") as f:
        comfy_json = json.load(f)

    rf_graph = comfy_to_react_flow(comfy_json)
    assert isinstance(rf_graph, ReactFlowGraph)
    assert len(rf_graph.nodes) == 7  # Nodes 3, 4, 5, 6, 7, 8, 9
    assert len(rf_graph.edges) == 9  # 4 to KSampler, 2 to CLIPs, 2 to VAE, 1 to SaveImage

    # Verify KSampler node (id: 3)
    ksampler_node = next(n for n in rf_graph.nodes if n.id == "3")
    assert ksampler_node.data.class_type == "KSampler"
    assert ksampler_node.data.parameters["steps"] == 20
    assert ksampler_node.data.parameters["cfg"] == 8.0
    assert ksampler_node.data.parameters["sampler_name"] == "euler"
    assert ksampler_node.data.parameters["scheduler"] == "normal"
    # Connected links must not be inside parameters
    assert "model" not in ksampler_node.data.parameters
    assert "latent_image" not in ksampler_node.data.parameters

    # Verify edges targeting KSampler
    ksampler_in_edges = [e for e in rf_graph.edges if e.target == "3"]
    assert len(ksampler_in_edges) == 4
    edge_map = {e.targetHandle: (e.source, e.sourceHandle) for e in ksampler_in_edges}
    assert edge_map["input_model"] == ("4", "output_0")
    assert edge_map["input_latent_image"] == ("5", "output_0")
    assert edge_map["input_positive"] == ("6", "output_0")
    assert edge_map["input_negative"] == ("7", "output_0")


def test_hierarchical_layout_ranking():
    """Verifies that topological ranks and X/Y coordinates prevent overlaps."""
    preset_path = PRESETS_DIR / "default_txt2img.json"
    rf_graph = comfy_to_react_flow(preset_path)

    node_pos = {n.id: n.position for n in rf_graph.nodes}

    # Roots: CheckpointLoaderSimple (4) and EmptyLatentImage (5) should be in layer 0
    assert node_pos["4"].x == 60.0
    assert node_pos["5"].x == 60.0
    # Vertically separated
    assert node_pos["4"].y != node_pos["5"].y

    # CLIPTextEncode (6 and 7) depend on CheckpointLoaderSimple (4) -> layer 1
    assert node_pos["6"].x > node_pos["4"].x
    assert node_pos["7"].x > node_pos["4"].x

    # KSampler (3) depends on CLIPTextEncode -> layer 2
    assert node_pos["3"].x > node_pos["6"].x

    # VAEDecode (8) depends on KSampler -> layer 3
    assert node_pos["8"].x > node_pos["3"].x

    # SaveImage (9) depends on VAEDecode -> layer 4
    assert node_pos["9"].x > node_pos["8"].x


# =========================================================================
# 4. Transpiler: react_flow_to_comfy & 100% Roundtrip Equivalence
# =========================================================================

@pytest.mark.parametrize("preset_filename", [
    "default_txt2img.json",
    "match3_gem_icons_sdxl.json",
    "game_hero_portrait_flux.json",
    "controlnet_canny_layout.json",
    "ipadapter_gamedna_consistency.json",
])
def test_bidirectional_roundtrip_equivalence(preset_filename):
    """
    Kabul Kriteri: Geçerli bir ComfyUI API JSON dosyası comfy_to_react_flow ile çevrilip
    tekrar react_flow_to_comfy yapıldığında orijinal JSON ile mantıksal olarak %100 özdeş olmalıdır.
    """
    preset_path = PRESETS_DIR / preset_filename
    with open(preset_path, "r", encoding="utf-8") as f:
        original_comfy = json.load(f)

    # 1. Comfy -> React Flow
    rf_graph = comfy_to_react_flow(original_comfy)

    # 2. React Flow -> Comfy
    reconstructed_comfy = react_flow_to_comfy(rf_graph)

    # 3. Structural equivalence check
    assert set(reconstructed_comfy.keys()) == set(original_comfy.keys()), (
        f"Node keys mismatch for {preset_filename}"
    )

    for node_id, orig_node in original_comfy.items():
        recon_node = reconstructed_comfy[node_id]
        assert recon_node["class_type"] == orig_node["class_type"]

        orig_inputs = orig_node.get("inputs", {})
        recon_inputs = recon_node.get("inputs", {})

        assert set(recon_inputs.keys()) == set(orig_inputs.keys()), (
            f"Inputs keys mismatch on node {node_id} in {preset_filename}"
        )

        for input_key, orig_val in orig_inputs.items():
            recon_val = recon_inputs[input_key]
            # Link comparison: [source_id, output_idx]
            if isinstance(orig_val, list):
                # Ensure source_id as str comparison
                assert [str(recon_val[0]), int(recon_val[1])] == [str(orig_val[0]), int(orig_val[1])]
            else:
                assert recon_val == orig_val


# =========================================================================
# 5. Missing Required Port Tests
# =========================================================================

def test_missing_required_port_error():
    """Verifies that an unconnected required port raises ComfyMissingPortError."""
    preset_path = PRESETS_DIR / "default_txt2img.json"
    with open(preset_path, "r", encoding="utf-8") as f:
        comfy_json = json.load(f)

    rf_graph = comfy_to_react_flow(comfy_json)

    # Remove the edge supplying 'model' to KSampler (node '3')
    rf_graph.edges = [
        e for e in rf_graph.edges
        if not (e.target == "3" and e.targetHandle == "input_model")
    ]

    with pytest.raises(ComfyMissingPortError) as exc_info:
        react_flow_to_comfy(rf_graph, validate_required=True)

    err = exc_info.value
    assert err.node_id == "3"
    assert err.class_type == "KSampler"
    assert err.input_name == "model"
    assert err.expected_type == "MODEL"


# =========================================================================
# 6. Validator: Edge Type Compatibility Tests
# =========================================================================

def test_validate_comfy_edge_success():
    """Verifies valid port connections pass without error."""
    extractor = ComfySchemaExtractor()

    # MODEL -> MODEL
    assert validate_comfy_edge(
        source_node={"id": "1", "class_type": "CheckpointLoaderSimple"},
        target_node={"id": "2", "class_type": "KSampler"},
        source_handle="output_0",  # MODEL
        target_handle="input_model",  # MODEL
        schema_extractor=extractor,
    )

    # CONDITIONING -> CONDITIONING
    assert validate_comfy_edge(
        source_node={"id": "3", "class_type": "CLIPTextEncode"},
        target_node={"id": "2", "class_type": "KSampler"},
        source_handle="output_0",  # CONDITIONING
        target_handle="input_positive",  # CONDITIONING
        schema_extractor=extractor,
    )


def test_validate_comfy_edge_type_mismatch():
    """
    Kabul Kriteri: Hatalı bir bağlantı (ör. IMAGE portundan MODEL girişine)
    açık bir tip hatası (ComfyTypeMismatchError) üretmelidir.
    """
    extractor = ComfySchemaExtractor()

    # Attempt to connect VAEDecode output (IMAGE) to KSampler input (MODEL)
    with pytest.raises(ComfyTypeMismatchError) as exc_info:
        validate_comfy_edge(
            source_node={"id": "8", "class_type": "VAEDecode"},
            target_node={"id": "3", "class_type": "KSampler"},
            source_handle="output_0",  # IMAGE
            target_handle="input_model",  # MODEL
            schema_extractor=extractor,
        )

    err = exc_info.value
    assert err.source_type == "IMAGE"
    assert err.target_type == "MODEL"
    assert err.source_node == "8"
    assert err.target_node == "3"
    assert "IMAGE" in str(err)
    assert "MODEL" in str(err)


# =========================================================================
# 7. Validator: DAG Cycle Detection Tests
# =========================================================================

def test_detect_cycles_in_dag():
    """Verifies acyclic graphs return None, while cycles raise ComfyCycleError."""
    # Acyclic: 1 -> 2 -> 3
    nodes = ["1", "2", "3"]
    acyclic_edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
    ]
    assert detect_cycles(nodes, acyclic_edges) is None

    # Cyclic: 1 -> 2 -> 3 -> 1
    cyclic_edges = [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"},
        {"source": "3", "target": "1"},
    ]
    cycle = detect_cycles(nodes, cyclic_edges)
    assert cycle is not None
    assert len(cycle) >= 3

    # Self-loop: 1 -> 1
    self_loop = [{"source": "1", "target": "1"}]
    assert detect_cycles(["1"], self_loop) is not None


def test_validate_workflow_graph_cycle_error():
    """Verifies validate_workflow_graph raises ComfyCycleError when cycle exists."""
    rf_graph = ReactFlowGraph(
        nodes=[
            ReactFlowNode(
                id="1",
                position=Position(x=0, y=0),
                data=ReactFlowNodeData(id="1", label="Checkpoint", class_type="CheckpointLoaderSimple"),
            ),
            ReactFlowNode(
                id="2",
                position=Position(x=300, y=0),
                data=ReactFlowNodeData(id="2", label="KSampler", class_type="KSampler"),
            ),
        ],
        edges=[
            ReactFlowEdge(id="e1", source="1", target="2", sourceHandle="output_0", targetHandle="input_model"),
            ReactFlowEdge(id="e2", source="2", target="1", sourceHandle="output_0", targetHandle="input_model"),
        ],
    )

    with pytest.raises(ComfyCycleError):
        validate_workflow_graph(rf_graph, check_required=False)


def test_validate_workflow_graph_complete_preset_passes():
    """Verifies that all 5 preset workflows pass validation completely."""
    for preset_name in [
        "default_txt2img.json",
        "match3_gem_icons_sdxl.json",
        "game_hero_portrait_flux.json",
        "controlnet_canny_layout.json",
        "ipadapter_gamedna_consistency.json",
    ]:
        preset_file = PRESETS_DIR / preset_name
        rf_graph = comfy_to_react_flow(preset_file)
        result = validate_workflow_graph(rf_graph, check_required=True)
        assert result.is_valid is True
        assert len(result.errors) == 0
