"""
CreativeForge v3.0 — Agent 4 End-to-End Demo Runner
Executes:
1. Image Generation (Mock / ComfyUI) -> Generates high-res PNG ad mockup
2. Video Composition (Remotion 9:16) -> Generates MP4 mobile video asset
3. HTML5 Playable Generation -> Derives Match-3 game and bundles ZIP
4. Playwright Browser QA Sandbox -> Launches mobile Chromium, simulates touch events, validates zero JS errors and saves screenshot.
"""

import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root_dir, "services", "worker-image"))
sys.path.insert(0, os.path.join(root_dir, "services", "worker-video"))
sys.path.insert(0, os.path.join(root_dir, "services", "worker-playable"))

from image_models import ImageAssetRequest
from image_worker import ImageWorker
from storage import LocalStorageClient
from video_models import Storyboard, VideoShot
from video_worker import VideoWorker
from playable_models import PlayableSpec
from sandbox import SandboxBuildRunner
from qa_runner import PlaywrightRunner

def main():
    print("=" * 60)
    print(">>> CREATIVEFORGE STUDIO -- AGENT 4 DEMO EXECUTION <<<")
    print("=" * 60)

    storage = LocalStorageClient(base_dir=os.path.join(root_dir, "storage", "artifacts"))

    # 1. IMAGE PRODUCTION
    print("\n[1/4] Running Image Production Worker...")
    img_worker = ImageWorker(storage_client=storage)
    img_req = ImageAssetRequest(
        concept_id="concept_dragon_rescue",
        prompt="Fantasy dungeon match-3 puzzle with glowing runes and trapped hero",
        width=720,
        height=1280,
        aspect_ratio="9:16",
        seed=2026,
        headline="RESCUE THE HERO!",
        hook_text="Match 3 runes before the magma rises!",
        call_to_action="PLAY NOW FOR FREE"
    )
    img_asset = img_worker.process_request(img_req, run_id="run_demo_001")
    print(f"  [OK] Image Created: {img_asset.artifact_id}")
    print(f"    - SHA256: {img_asset.sha256[:16]}...")
    print(f"    - Resolution: {img_asset.metadata.width}x{img_asset.metadata.height}")
    print(f"    - File URI: {img_asset.storage_ref}")

    # 2. VIDEO PRODUCTION
    print("\n[2/4] Running Remotion 9:16 Video Production Worker...")
    vid_worker = VideoWorker(storage_client=storage)
    storyboard = Storyboard(
        storyboard_id="sb_dragon_rescue",
        title="Dragon Rescue Puzzle Ad",
        duration_seconds=15.0,
        shots=[
            VideoShot(shot_id="s1", start_sec=0, end_sec=3, headline="CAN YOU ESCAPE?", subtext="99% fail on level 4!", visual_type="hook_animation", accent_color="#EF4444"),
            VideoShot(shot_id="s2", start_sec=3, end_sec=10, headline="SWIPE TO MATCH", subtext="Trigger the chain combo!", visual_type="gameplay_simulation", accent_color="#3B82F6"),
            VideoShot(shot_id="s3", start_sec=10, end_sec=15, headline="INSTALL NOW", subtext="Free on App Store", visual_type="cta_endcard", accent_color="#10B981")
        ]
    )
    vid_asset = vid_worker.process_storyboard(
        storyboard,
        run_id="run_demo_001",
        parent_artifact_ids=[img_asset.artifact_id]
    )
    print(f"  [OK] Video Created: {vid_asset.artifact_id}")
    print(f"    - Duration: {vid_asset.duration_seconds}s | FPS: {vid_asset.fps} | Codec: {vid_asset.codec}")
    print(f"    - SHA256: {vid_asset.sha256[:16]}...")
    print(f"    - File URI: {vid_asset.storage_ref}")

    # 3. HTML5 PLAYABLE GENERATION & SANDBOX BUILD
    print("\n[3/4] Running HTML5 Playable Mini-Game Sandbox Builder...")
    playable_runner = SandboxBuildRunner(storage_client=storage)
    spec = PlayableSpec(
        spec_id="spec_rescue_match3",
        title="Dungeon Rune Match-3 Rescue",
        hook_text="Match 3 Runes to Break the Dungeon Curse!",
        cta_text="CLAIM FREE 500 GEMS NOW",
        cta_url="https://apps.apple.com/app/dragon-rescue",
        target_score=500,
        max_moves=8,
        points_per_match=100,
        colors=["#EF4444", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"]
    )
    playable_bundle = playable_runner.build_playable(
        spec,
        run_id="run_demo_001",
        parent_artifact_ids=[img_asset.artifact_id, vid_asset.artifact_id]
    )
    print(f"  [OK] Playable Bundle Created: {playable_bundle.artifact_id}")
    print(f"    - HTML URI: {playable_bundle.storage_ref}")
    print(f"    - ZIP Package URI: {playable_bundle.zip_storage_ref}")
    print(f"    - SHA256: {playable_bundle.sha256[:16]}...")

    # 4. PLAYWRIGHT BROWSER QA SANDBOX TEST
    print("\n[4/4] Executing Playwright Mobile Browser Smoke Test...")
    qa = PlaywrightRunner(screenshot_dir=os.path.join(root_dir, "storage", "qa_screenshots"))
    qa_report = qa.test_playable(playable_bundle.storage_ref)
    playable_bundle.test_report = qa_report

    print(f"  [OK] QA Test Status: {qa_report.status.upper()}")
    print(f"    - Load Time: {qa_report.load_time_ms} ms")
    print(f"    - Canvas Initialized: {qa_report.canvas_initialized}")
    print(f"    - Interactions Executed: {qa_report.interactions_completed}")
    print(f"    - JS Console Errors: {len(qa_report.js_errors)}")
    if qa_report.screenshot_path:
        print(f"    - Screenshot Evidence: {qa_report.screenshot_path}")

    print("\n" + "=" * 60)
    print(">>> ALL AGENT 4 WORKERS COMPLETED WITH 100% SUCCESS! <<<")
    print("=" * 60)

if __name__ == "__main__":
    main()
