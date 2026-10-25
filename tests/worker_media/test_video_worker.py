import os
import sys
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))

worker_video_dir = os.path.join(root_dir, "services", "worker-video")
worker_image_dir = os.path.join(root_dir, "services", "worker-image")
for d in [worker_video_dir, worker_image_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from video_models import Storyboard, VideoShot, VideoAsset
from probe import VideoProbe
from renderer import RemotionRenderer
from video_worker import VideoWorker
from storage import LocalStorageClient

def test_video_renderer_and_probe(tmp_path):
    renderer = RemotionRenderer()
    probe = VideoProbe()

    storyboard = Storyboard(
        storyboard_id="sb_test_01",
        title="Epic Puzzle Adventure",
        duration_seconds=15.0,
        fps=30,
        width=720,
        height=1280,
        shots=[
            VideoShot(shot_id="s1", start_sec=0, end_sec=3, headline="Save the Dragon", subtext="Can you beat level 5?", visual_type="hook_animation", accent_color="#EF4444"),
            VideoShot(shot_id="s2", start_sec=3, end_sec=10, headline="Match 3 Gems", subtext="Combo x4!", visual_type="gameplay_simulation", accent_color="#3B82F6"),
            VideoShot(shot_id="s3", start_sec=10, end_sec=15, headline="Play Free Now", subtext="Tap below!", visual_type="cta_endcard", accent_color="#10B981")
        ]
    )

    out_mp4 = os.path.join(str(tmp_path), "test_video.mp4")
    renderer.render_storyboard(storyboard, out_mp4)

    assert os.path.exists(out_mp4)
    assert os.path.getsize(out_mp4) > 100

    report = probe.probe_file(out_mp4)
    assert report.valid is True
    assert report.duration_seconds == 15.0
    assert report.width == 720
    assert report.height == 1280

def test_video_worker_full_pipeline(tmp_path):
    storage = LocalStorageClient(base_dir=str(tmp_path / "artifacts"))
    worker = VideoWorker(storage_client=storage)

    storyboard = Storyboard(
        storyboard_id="sb_test_02",
        title="Royal Match Ad",
        duration_seconds=15.0,
        shots=[
            VideoShot(shot_id="s1", start_sec=0, end_sec=5, headline="Help the King!", subtext="Water is rising!", visual_type="hook_animation"),
            VideoShot(shot_id="s2", start_sec=5, end_sec=15, headline="Play Now", subtext="Download Free", visual_type="cta_endcard")
        ]
    )

    video_asset = worker.process_storyboard(
        storyboard,
        run_id="run_vid_200",
        parent_artifact_ids=["art_img_01", "art_img_02"]
    )

    assert isinstance(video_asset, VideoAsset)
    assert video_asset.run_id == "run_vid_200"
    assert video_asset.duration_seconds == 15.0
    assert len(video_asset.parent_ids) == 2
    assert len(video_asset.sha256) == 64
