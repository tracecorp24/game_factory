from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

try:
    from ..image_models import ImageAssetRequest
except (ImportError, ValueError):
    from image_models import ImageAssetRequest

class BaseImageAdapter(ABC):
    @abstractmethod
    def generate(self, request: ImageAssetRequest) -> Tuple[bytes, Dict[str, Any]]:
        pass
