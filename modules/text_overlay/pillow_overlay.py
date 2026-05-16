"""
modules/text_overlay/pillow_overlay.py
=======================================
Text overlay module using Pillow (PIL).
Whites out the original bubble area and draws wrapped English text.

Install:  pip install Pillow
"""

from __future__ import annotations
import logging
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from core.interfaces import BaseTextOverlay, TextRegion

logger = logging.getLogger(__name__)

# Bundled fallback font path (place a .ttf here or set font_path in config)
_DEFAULT_FONT = Path(__file__).parent / "fonts" / "ComicNeue-Bold.ttf"


class PillowOverlay(BaseTextOverlay):
    """
    For each TextRegion:
      1. Fill the bounding box with bg_color (white by default)
      2. Draw a thin border so the bubble outline is preserved
      3. Word-wrap and center the translated text inside the box

    Config options (overlay_options in config.yaml):
      font_path  : path to a .ttf file (null = use system default)
      font_size  : base font size in pixels
      text_color : [R, G, B]
      bg_color   : [R, G, B]
    """

    def __init__(
        self,
        font_path:  str | None   = None,
        font_size:  int          = 14,
        text_color: list[int]    = None,
        bg_color:   list[int]    = None,
        **kwargs,
    ):
        self.font_size  = font_size
        self.text_color = tuple(text_color or [0, 0, 0])
        self.bg_color   = tuple(bg_color   or [255, 255, 255])
        self._font_path = font_path
        self._font_cache: dict[int, ImageFont.FreeTypeFont] = {}

    # ── Font loading ──────────────────────────────────────────────────────────

    def _get_font(self, size: int) -> ImageFont.ImageFont:
        if size not in self._font_cache:
            path = self._font_path or str(_DEFAULT_FONT)
            try:
                self._font_cache[size] = ImageFont.truetype(path, size)
            except (IOError, OSError):
                logger.warning(f"[Overlay] Font not found at {path}, using default")
                self._font_cache[size] = ImageFont.load_default()
        return self._font_cache[size]

    # ── Main apply ────────────────────────────────────────────────────────────

    def apply(self, image: Image.Image, regions: list[TextRegion]) -> Image.Image:
        # Work on a copy — never mutate the input
        result = image.copy().convert("RGB")
        draw   = ImageDraw.Draw(result)

        for region in regions:
            if not region.translated_text.strip():
                continue

            b = region.bbox
            # 1. Fill box with background colour
            draw.rectangle([b.x, b.y, b.x + b.w, b.y + b.h], fill=self.bg_color)

            # 2. Fit text to box
            font, lines = self._fit_text(region.translated_text, b.w, b.h)

            # 3. Draw centred text
            line_height = font.size + 3
            total_h     = len(lines) * line_height
            start_y     = b.y + (b.h - total_h) // 2

            for i, line in enumerate(lines):
                bbox_line = draw.textbbox((0, 0), line, font=font)
                line_w    = bbox_line[2] - bbox_line[0]
                x         = b.x + (b.w - line_w) // 2
                y         = start_y + i * line_height
                draw.text((x, y), line, font=font, fill=self.text_color)

        return result

    # ── Text fitting helpers ──────────────────────────────────────────────────

    def _fit_text(
        self,
        text: str,
        box_w: int,
        box_h: int,
    ) -> tuple[ImageFont.ImageFont, list[str]]:
        """
        Tries decreasing font sizes until the wrapped text fits in the box.
        Returns (font, list_of_lines).
        """
        for size in range(self.font_size, 7, -1):
            font = self._get_font(size)
            lines = self._wrap(text, font, box_w - 8)   # 4px padding each side
            total_h = len(lines) * (size + 3)
            if total_h <= box_h - 8:
                return font, lines

        # Last resort: smallest size, may overflow
        font = self._get_font(8)
        return font, self._wrap(text, font, box_w - 8)

    @staticmethod
    def _wrap(text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
        """Word-wrap text to fit within max_width pixels."""
        words  = text.split()
        lines  = []
        current = ""

        # Use a dummy ImageDraw to measure text width
        dummy = ImageDraw.Draw(Image.new("RGB", (1, 1)))

        for word in words:
            test = (current + " " + word).strip()
            w = dummy.textbbox((0, 0), test, font=font)[2]
            if w <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines or [text]
