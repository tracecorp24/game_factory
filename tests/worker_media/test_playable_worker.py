import os
import sys
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))

worker_playable_dir = os.path.join(root_dir, "services", "worker-playable")
worker_image_dir = os.path.join(root_dir, "services", "worker-image")
for d in [worker_playable_dir, worker_image_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from playable_models import PlayableSpec, PlayableBundle, BrowserTestReport
from generator import PlayableCodeGenerator
from sandbox import SandboxBuildRunner
from qa_runner import PlaywrightRunner
from storage import LocalStorageClient

def test_playable_code_generator():
    generator = PlayableCodeGenerator()
    spec = PlayableSpec(
        spec_id="spec_test_01",
        title="Candy Crush Ad Demo",
        hook_text="Swipe to blast candies!",
        cta_text="DOWNLOAD NOW",
        target_score=500,
        max_moves=6
    )

    zip_bytes, html_content = generator.generate_zip_package(spec)

    assert "Candy Crush Ad Demo" in html_content
    assert "Swipe to blast candies!" in html_content
    assert "DOWNLOAD NOW" in html_content
    assert "500" in html_content
    assert len(zip_bytes) > 1000

def test_sandbox_build_runner(tmp_path):
    storage = LocalStorageClient(base_dir=str(tmp_path / "artifacts"))
    runner = SandboxBuildRunner(storage_client=storage)

    spec = PlayableSpec(
        spec_id="spec_test_02",
        title="Match 3 Kingdom Rescue",
        hook_text="Can you save the realm?",
        target_score=800,
        max_moves=10
    )

    bundle = runner.build_playable(spec, run_id="run_play_300")

    assert isinstance(bundle, PlayableBundle)
    assert bundle.run_id == "run_play_300"
    assert bundle.entrypoint == "index.html"
    assert len(bundle.sha256) == 64
    assert bundle.build_report["status"] == "success"
    assert bundle.zip_storage_ref is not None

def test_playwright_qa_runner(tmp_path):
    storage = LocalStorageClient(base_dir=str(tmp_path / "artifacts"))
    runner = SandboxBuildRunner(storage_client=storage)
    qa = PlaywrightRunner(screenshot_dir=str(tmp_path / "qa_screens"))

    spec = PlayableSpec(
        spec_id="spec_test_qa",
        title="QA Test Mini Game",
        hook_text="Test the match mechanics!",
        target_score=300,
        max_moves=5
    )

    bundle = runner.build_playable(spec)
    report = qa.test_playable(bundle.storage_ref)

    assert isinstance(report, BrowserTestReport)
    assert report.status == "passed"
    assert len(report.js_errors) == 0
    assert report.canvas_initialized is True
    assert report.interactions_completed >= 2
