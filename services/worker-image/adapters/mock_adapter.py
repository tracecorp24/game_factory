import io
import math
import random
from typing import Tuple, Dict, Any
from PIL import Image, ImageDraw, ImageFont

try:
    from .base import BaseImageAdapter
    from ..image_models import ImageAssetRequest
except (ImportError, ValueError):
    from adapters.base import BaseImageAdapter
    from image_models import ImageAssetRequest

class MockImageAdapter(BaseImageAdapter):
    def __init__(self, brand_name: str = "CreativeForge Studio"):
        self.brand_name = brand_name

    def generate(self, request: ImageAssetRequest) -> Tuple[bytes, Dict[str, Any]]:
        w = max(request.width, 400)
        h = max(request.height, 400)
        
        seed = request.seed if request.seed is not None else 42
        rng = random.Random(seed)

        img = Image.new("RGBA", (w, h), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)

        bg_colors = [
            (24, 24, 48), (30, 41, 59), (15, 23, 42), (49, 46, 129), (13, 148, 136)
        ]
        primary_color = rng.choice(bg_colors)
        
        for y in range(h):
            factor = y / h
            r = int(primary_color[0] * (1 - factor) + 15 * factor)
            g = int(primary_color[1] * (1 - factor) + 23 * factor)
            b = int(primary_color[2] * (1 - factor) + 42 * factor)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

        grid_size = min(w, h) // 2
        gx = (w - grid_size) // 2
        gy = (h - grid_size) // 2 + 20
        
        cell_count = 4
        cell_size = grid_size // cell_count
        gem_palette = [
            (239, 68, 68), (59, 130, 246), (16, 185, 129), (245, 158, 11), (139, 92, 246)
        ]

        draw.rounded_rectangle(
            [(gx - 12, gy - 12), (gx + grid_size + 12, gy + grid_size + 12)],
            radius=16,
            fill=(30, 41, 59, 220),
            outline=(56, 189, 248, 255),
            width=2
        )

        for row in range(cell_count):
            for col in range(cell_count):
                cx = gx + col * cell_size
                cy = gy + row * cell_size
                gem_color = rng.choice(gem_palette)
                
                pad = 6
                draw.rounded_rectangle(
                    [(cx + pad, cy + pad), (cx + cell_size - pad, cy + cell_size - pad)],
                    radius=8,
                    fill=gem_color,
                    outline=(255, 255, 255, 120),
                    width=2
                )
                draw.ellipse(
                    [(cx + pad + 3, cy + pad + 3), (cx + pad + cell_size // 3, cy + pad + cell_size // 4)],
                    fill=(255, 255, 255, 180)
                )

        headline_text = (request.headline or "CRITICAL PUZZLE RESCUE").upper()
        draw.rectangle([(0, 40), (w, 110)], fill=(0, 0, 0, 160))
        draw.text((w // 2, 60), headline_text, fill=(255, 255, 255, 255), anchor="mm")
        
        hook_text = request.hook_text or "Match 3 to break the curse!"
        draw.rounded_rectangle(
            [(w // 2 - 180, gy - 50), (w // 2 + 180, gy - 15)],
            radius=16,
            fill=(239, 68, 68, 240),
            outline=(254, 240, 138, 255),
            width=2
        )
        draw.text((w // 2, gy - 32), hook_text, fill=(255, 255, 255, 255), anchor="mm")

        cta_text = (request.call_to_action or "INSTALL NOW - FREE").upper()
        btn_y = gy + grid_size + 40
        draw.rounded_rectangle(
            [(w // 2 - 160, btn_y), (w // 2 + 160, btn_y + 50)],
            radius=25,
            fill=(16, 185, 129, 255),
            outline=(255, 255, 255, 200),
            width=2
        )
        draw.text((w // 2, btn_y + 25), cta_text, fill=(255, 255, 255, 255), anchor="mm")

        watermark = f"[MOCK-PROVIDER] {self.brand_name} • Seed: {seed} • Res: {w}x{h}"
        draw.text((w // 2, h - 20), watermark, fill=(148, 163, 184, 180), anchor="mm")

        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        raw_bytes = buf.getvalue()

        metadata = {
            "adapter": "MockImageAdapter",
            "seed": seed,
            "width": w,
            "height": h,
            "aspect_ratio": request.aspect_ratio,
            "format": "PNG",
            "size_bytes": len(raw_bytes),
            "generated_with": "Pillow Canvas Synthetic Renderer"
        }

        return raw_bytes, metadata
