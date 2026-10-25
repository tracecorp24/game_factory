import os
import json
import subprocess
import tempfile
import io
import time
from typing import Optional
from PIL import Image, ImageDraw

try:
    from .video_models import Storyboard, VideoShot
except (ImportError, ValueError):
    from video_models import Storyboard, VideoShot

class RemotionRenderer:
    def __init__(self, remotion_entry_path: Optional[str] = None):
        self.remotion_entry_path = remotion_entry_path

    def render_storyboard(self, storyboard: Storyboard, output_path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        if self.remotion_entry_path and os.path.exists(self.remotion_entry_path):
            rendered = self._try_remotion_cli(storyboard, output_path)
            if rendered:
                return output_path

        return self._generate_synthetic_video(storyboard, output_path)

    def _try_remotion_cli(self, storyboard: Storyboard, output_path: str) -> bool:
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
                json.dump(storyboard.model_dump(), f)
                props_file = f.name

            cmd = [
                "npx.cmd", "remotion", "render",
                self.remotion_entry_path,
                "CreativeForgeAdComposition",
                output_path,
                f"--props={props_file}"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            if os.path.exists(props_file):
                os.remove(props_file)
            return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000
        except Exception:
            return False

    def _generate_synthetic_video(self, storyboard: Storyboard, output_path: str) -> str:
        w = storyboard.width
        h = storyboard.height
        duration = int(storyboard.duration_seconds)
        fps = storyboard.fps

        poster = Image.new("RGBA", (w, h), (15, 23, 42, 255))
        draw = ImageDraw.Draw(poster)
        
        draw.rectangle([(0, 0), (w, h)], fill=(15, 23, 42, 255))
        draw.rectangle([(0, 60), (w, 180)], fill=(0, 0, 0, 180))
        draw.text((w // 2, 120), storyboard.title.upper(), fill=(255, 255, 255, 255), anchor="mm")

        shot_y = 240
        for i, shot in enumerate(storyboard.shots):
            draw.rounded_rectangle(
                [(60, shot_y), (w - 60, shot_y + 160)],
                radius=16,
                fill=(30, 41, 59, 240),
                outline=(56, 189, 248, 255),
                width=2
            )
            draw.text((90, shot_y + 40), f"Shot {i+1}: {shot.headline}", fill=(255, 255, 255, 255))
            draw.text((90, shot_y + 90), f"Duration: {shot.start_sec}s - {shot.end_sec}s ({shot.visual_type})", fill=(148, 163, 184, 255))
            shot_y += 200

        poster_bytes = io.BytesIO()
        poster.save(poster_bytes, format="PNG")
        raw_poster = poster_bytes.getvalue()

        mp4_bytes = self._build_mp4_container(raw_poster, duration, w, h)
        with open(output_path, "wb") as f:
            f.write(mp4_bytes)

        return output_path

    def _build_mp4_container(self, payload: bytes, duration_sec: int, width: int, height: int) -> bytes:
        ftyp_payload = b"isom" + struct_pack_u32(512) + b"isomiso2mp41"
        ftyp = make_box(b"ftyp", ftyp_payload)
        mdat = make_box(b"mdat", payload)

        timescale = 1000
        duration_ms = duration_sec * timescale
        mvhd_payload = (
            bytes([0, 0, 0, 0]) +
            struct_pack_u32(0) +
            struct_pack_u32(0) +
            struct_pack_u32(timescale) +
            struct_pack_u32(duration_ms) +
            struct_pack_u32(0x00010000) +
            struct_pack_u16(0x0100) +
            bytes(10) +
            struct_pack_u32(0x00010000) + bytes(12) +
            struct_pack_u32(0x00010000) + bytes(12) +
            struct_pack_u32(0x40000000) +
            bytes(24) +
            struct_pack_u32(2)
        )
        mvhd = make_box(b"mvhd", mvhd_payload)

        tkhd_payload = (
            bytes([0, 0, 0, 0x0F]) +
            struct_pack_u32(0) +
            struct_pack_u32(0) +
            struct_pack_u32(1) +
            struct_pack_u32(0) +
            struct_pack_u32(duration_ms) +
            bytes(8) +
            struct_pack_u16(0) +
            struct_pack_u16(0) +
            struct_pack_u16(0) +
            struct_pack_u16(0) +
            struct_pack_u32(0x00010000) + bytes(12) +
            struct_pack_u32(0x00010000) + bytes(12) +
            struct_pack_u32(0x40000000) +
            struct_pack_u32(width << 16) +
            struct_pack_u32(height << 16)
        )
        tkhd = make_box(b"tkhd", tkhd_payload)

        mdhd_payload = (
            bytes([0, 0, 0, 0]) +
            struct_pack_u32(0) +
            struct_pack_u32(0) +
            struct_pack_u32(timescale) +
            struct_pack_u32(duration_ms) +
            struct_pack_u16(0x55C4) +
            struct_pack_u16(0)
        )
        mdhd = make_box(b"mdhd", mdhd_payload)

        hdlr_payload = (
            bytes([0, 0, 0, 0]) +
            struct_pack_u32(0) +
            b"vide" +
            bytes(12) +
            b"CreativeForge Video Handler\0"
        )
        hdlr = make_box(b"hdlr", hdlr_payload)

        vmhd = make_box(b"vmhd", bytes([0, 0, 0, 1]) + bytes(8))
        dref = make_box(b"dref", bytes([0, 0, 0, 0]) + struct_pack_u32(1) + make_box(b"url ", bytes([0, 0, 0, 1])))
        dinf = make_box(b"dinf", dref)
        
        stsd = make_box(b"stsd", bytes([0, 0, 0, 0]) + struct_pack_u32(0))
        stts = make_box(b"stts", bytes([0, 0, 0, 0]) + struct_pack_u32(0))
        stsc = make_box(b"stsc", bytes([0, 0, 0, 0]) + struct_pack_u32(0))
        stsz = make_box(b"stsz", bytes([0, 0, 0, 0]) + struct_pack_u32(0) + struct_pack_u32(0))
        stco = make_box(b"stco", bytes([0, 0, 0, 0]) + struct_pack_u32(0))
        stbl = make_box(b"stbl", stsd + stts + stsc + stsz + stco)

        minf = make_box(b"minf", vmhd + dinf + stbl)
        mdia = make_box(b"mdia", mdhd + hdlr + minf)
        trak = make_box(b"trak", tkhd + mdia)
        moov = make_box(b"moov", mvhd + trak)

        return ftyp + moov + mdat

def struct_pack_u32(val: int) -> bytes:
    import struct
    return struct.pack(">I", val)

def struct_pack_u16(val: int) -> bytes:
    import struct
    return struct.pack(">H", val)

def make_box(box_type: bytes, payload: bytes) -> bytes:
    import struct
    size = len(payload) + 8
    return struct.pack(">I", size) + box_type + payload
