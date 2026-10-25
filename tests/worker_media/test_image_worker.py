import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))

worker_image_dir = os.path.join(root_dir, "services", "worker-image")
if worker_image_dir not in sys.path:
    sys.path.insert(0, worker_image_dir)

from image_models import ImageAssetRequest, ImageAsset
from storage import LocalStorageClient
from adapters.mock_adapter import MockImageAdapter
from image_worker import ImageWorker

def test_mock_image_adapter_generation():
    adapter = MockImageAdapter(brand_name="TestStudio")
    req = ImageAssetRequest(
        concept_id="concept_gem_01",
        prompt="A fantasy match-3 gem cave with glowing rubies",
        width=512,
        height=512,
        aspect_ratio="1:1",
        seed=12345,
        headline="Cave of Jewels",
        hook_text="Match 3 to escape!"
    )
    png_bytes, meta = adapter.generate(req)

    assert len(png_bytes) > 1000
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"
    assert meta["width"] == 512
    assert meta["height"] == 512
    assert meta["seed"] == 12345

def test_image_worker_workflow(tmp_path):
    storage = LocalStorageClient(base_dir=str(tmp_path))
    worker = ImageWorker(storage_client=storage)

    req = ImageAssetRequest(
        concept_id="concept_02",
        prompt="Futuristic sci-fi sorting puzzle",
        width=600,
        height=800,
        aspect_ratio="3:4",
        seed=999
    )

    artifact = worker.process_request(req, run_id="run_test_100")

    assert isinstance(artifact, ImageAsset)
    assert artifact.run_id == "run_test_100"
    assert artifact.metadata.width == 600
    assert artifact.metadata.height == 800
    assert len(artifact.sha256) == 64
    assert artifact.bytes > 1000
    assert os.path.exists(artifact.storage_ref.replace("file:///", ""))
