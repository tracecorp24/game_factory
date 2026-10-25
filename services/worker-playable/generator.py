import os
import json
import zipfile
import io
from typing import Tuple, Dict, Any, Optional

try:
    from .playable_models import PlayableSpec
except (ImportError, ValueError):
    from playable_models import PlayableSpec

class PlayableCodeGenerator:
    def __init__(self, template_dir: Optional[str] = None):
        if template_dir:
            self.template_dir = os.path.abspath(template_dir)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.template_dir = os.path.abspath(
                os.path.join(current_dir, "..", "..", "packages", "media-presets", "playable-templates", "match3")
            )

    def load_template(self) -> str:
        template_file = os.path.join(self.template_dir, "index.html")
        if not os.path.exists(template_file):
            raise FileNotFoundError(f"Playable template not found at {template_file}")
        with open(template_file, "r", encoding="utf-8") as f:
            return f.read()

    def generate_html(self, spec: PlayableSpec) -> str:
        raw_template = self.load_template()

        replacements = {
            "{{TITLE}}": spec.title,
            "{{BACKGROUND_COLOR}}": spec.background_color,
            "{{ACCENT_COLOR}}": spec.accent_color,
            "{{HOOK_TEXT}}": spec.hook_text,
            "{{CTA_TEXT}}": spec.cta_text,
            "{{CTA_URL}}": spec.cta_url,
            "{{TARGET_SCORE}}": str(spec.target_score),
            "{{MAX_MOVES}}": str(spec.max_moves),
            "{{POINTS_PER_MATCH}}": str(spec.points_per_match),
            "{{COLORS_JSON}}": json.dumps(spec.colors)
        }

        html_output = raw_template
        for placeholder, value in replacements.items():
            html_output = html_output.replace(placeholder, value)

        return html_output

    def generate_zip_package(self, spec: PlayableSpec) -> Tuple[bytes, str]:
        html_content = self.generate_html(spec)
        manifest_data = {
            "spec_id": spec.spec_id,
            "title": spec.title,
            "template": spec.template_name,
            "entrypoint": "index.html",
            "version": "1.0.0",
            "viewport": {
                "width": 390,
                "height": 844,
                "responsive": True
            },
            "cta": {
                "url": spec.cta_url,
                "label": spec.cta_text
            }
        }

        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("index.html", html_content)
            zf.writestr("manifest.json", json.dumps(manifest_data, indent=2))

        zip_bytes = zip_buf.getvalue()
        return zip_bytes, html_content
