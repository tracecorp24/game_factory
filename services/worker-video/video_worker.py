import os
import sys
import uuid
import tempfile
from typing import Optional, List
import importlib

try:
    from .video_models import Storyboard, VideoAsset, VideoProbeReport
    from .probe import VideoProbe
    from .renderer import RemotionRenderer
except (ImportError, ValueError):
    from video_models import Storyboard, VideoAsset, VideoProbeReport
    from probe import VideoProbe
    from renderer import RemotionRenderer

current_dir = os.path.dirname(os.path.abspath(__file__))
image_worker_dir = os.path.abspath(os.path.join(current_dir, "..", "worker-image"))
if image_worker_dir not in sys.path:
    sys.path.insert(0, image_worker_dir)

try:
    from storage import BaseStorageClient, LocalStorageClient
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location("storage", os.path.join(image_worker_dir, "storage.py"))
    storage_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(storage_mod)
    BaseStorageClient = storage_mod.BaseStorageClient
    LocalStorageClient = storage_mod.LocalStorageClient

class VideoWorker:
    def __init__(
        self,
        storage_client: Optional[BaseStorageClient] = None,
        remotion_entry_path: Optional[str] = None
    ):
        self.storage = storage_client or LocalStorageClient(base_dir="./storage/artifacts")
        self.renderer = RemotionRenderer(remotion_entry_path=remotion_entry_path)
        self.probe = VideoProbe()

    def process_storyboard(
        self,
        storyboard: Storyboard,
        run_id: str = "run_default",
        parent_artifact_ids: Optional[List[str]] = None
    ) -> VideoAsset:
        call_id = f"vid_call_{uuid.uuid4().hex[:10]}"
        parent_ids = parent_artifact_ids or []

        temp_dir = tempfile.mkdtemp(prefix="cf_video_render_")
        temp_output_mp4 = os.path.join(temp_dir, f"{storyboard.storyboard_id}_final.mp4")

        try:
            self.renderer.render_storyboard(storyboard, temp_output_mp4)

            probe_report = self.probe.probe_file(temp_output_mp4)
            if not probe_report.valid:
                raise ValueError(f"Rendered video failed probe checks: {probe_report.issues}")

            with open(temp_output_mp4, "rb") as f:
                video_bytes = f.read()

            filename = f"{storyboard.storyboard_id}_9x16.mp4"
            storage_ref = self.storage.save_bytes(video_bytes, filename=filename, mime_type="video/mp4")
            preview_url = self.storage.get_preview_ticket(storage_ref.uri)

            resolution_str = f"{probe_report.width}x{probe_report.height}"

            artifact = VideoAsset(
                run_id=run_id,
                storyboard_id=storyboard.storyboard_id,
                storage_ref=storage_ref.uri,
                preview_url=preview_url,
                sha256=storage_ref.sha256,
                bytes=storage_ref.bytes,
                duration_seconds=probe_report.duration_seconds,
                fps=int(probe_report.fps),
                resolution=resolution_str,
                codec=probe_report.codec,
                aspect_ratio=storyboard.aspect_ratio,
                generation_call_id=call_id,
                parent_ids=parent_ids
            )

            return artifact

        finally:
            if os.path.exists(temp_output_mp4):
                try:
                    os.remove(temp_output_mp4)
                    os.rmdir(temp_dir)
                except Exception:
                    pass
