import io
import logging
import uuid
from typing import Any, Callable, Dict, Optional
from PIL import Image

try:
    from .image_models import ImageAssetRequest, ImageAsset, ImageMetadata
    from .storage import BaseStorageClient, LocalStorageClient
    from .adapters.base import BaseImageAdapter
    from .adapters.mock_adapter import MockImageAdapter
    from .adapters.comfyui_adapter import ComfyUIAdapter
    from .daemon import ComfyDaemonSupervisor
    from .template_engine import ComfyTemplateEngine
    from .ws_client import ComfyWebSocketListener
except (ImportError, ValueError):
    from image_models import ImageAssetRequest, ImageAsset, ImageMetadata
    from storage import BaseStorageClient, LocalStorageClient
    from adapters.base import BaseImageAdapter
    from adapters.mock_adapter import MockImageAdapter
    from adapters.comfyui_adapter import ComfyUIAdapter
    from daemon import ComfyDaemonSupervisor
    from template_engine import ComfyTemplateEngine
    from ws_client import ComfyWebSocketListener

logger = logging.getLogger("worker_image")


class ImageWorker:
    """
    Image generation worker supporting Local/Cloud Storage,
    ComfyUI Headless Daemon supervision, dynamic presets, and real-time WebSocket progress.
    """

    def __init__(
        self,
        storage_client: Optional[BaseStorageClient] = None,
        default_adapter: Optional[BaseImageAdapter] = None,
        comfyui_url: str = "http://127.0.0.1:8188",
        supervisor: Optional[ComfyDaemonSupervisor] = None,
    ):
        self.storage = storage_client or LocalStorageClient()
        self.mock_adapter = MockImageAdapter()
        self.comfyui_adapter = ComfyUIAdapter(base_url=comfyui_url)
        self.default_adapter = default_adapter or self.mock_adapter
        self.supervisor = supervisor
        self.template_engine = ComfyTemplateEngine()

    def process_request(
        self,
        request: ImageAssetRequest,
        run_id: str = "run_default",
        preset_name: Optional[str] = None,
        custom_variables: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, int, float, str], None]] = None,
    ) -> ImageAsset:
        call_id = f"img_call_{uuid.uuid4().hex[:10]}"

        if request.provider_preference == "comfyui":
            try:
                raw_bytes, prov_meta = self.comfyui_adapter.generate(
                    request=request,
                    preset_name=preset_name,
                    custom_variables=custom_variables,
                    progress_callback=progress_callback,
                )
                provider_name = "comfyui"
            except Exception as e:
                logger.warning(f"ComfyUI provider failed ({e}), falling back gracefully to MockImageAdapter")
                raw_bytes, prov_meta = self.mock_adapter.generate(request)
                provider_name = "mock_fallback"
        else:
            raw_bytes, prov_meta = self.mock_adapter.generate(request)
            provider_name = "mock"

        with Image.open(io.BytesIO(raw_bytes)) as pil_img:
            actual_w, actual_h = pil_img.size
            img_format = pil_img.format.lower() if pil_img.format else "png"
            channels = len(pil_img.getbands())
            has_alpha = "A" in pil_img.getbands()

        filename = f"{request.concept_id}_{request.width}x{request.height}.png"
        storage_ref = self.storage.save_bytes(raw_bytes, filename=filename, mime_type="image/png")
        preview_url = self.storage.get_preview_ticket(storage_ref.uri)

        metadata = ImageMetadata(
            width=actual_w,
            height=actual_h,
            aspect_ratio=request.aspect_ratio,
            format=img_format,
            channels=channels,
            has_alpha=has_alpha,
            color_palette=request.style_tokens,
        )

        artifact = ImageAsset(
            run_id=run_id,
            concept_id=request.concept_id,
            storage_ref=storage_ref.uri,
            preview_url=preview_url,
            sha256=storage_ref.sha256,
            bytes=storage_ref.bytes,
            metadata=metadata,
            generation_call_id=call_id,
            provider=provider_name,
            seed=request.seed,
            prompt_used=request.prompt,
            parent_ids=[request.concept_id],
        )

        return artifact

    def process_comfy_preset(
        self,
        preset_name: str,
        request: ImageAssetRequest,
        run_id: str = "run_default",
        custom_variables: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, int, float, str], None]] = None,
    ) -> ImageAsset:
        """Convenience method to execute a specific ComfyUI preset."""
        request.provider_preference = "comfyui"
        return self.process_request(
            request=request,
            run_id=run_id,
            preset_name=preset_name,
            custom_variables=custom_variables,
            progress_callback=progress_callback,
        )
