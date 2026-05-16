"""
modules/bubble_detection/manual_detector.py
===========================================
Manual bubble detector — you define the regions yourself in a JSON sidecar file.
Use this when OpenCV gives bad results on a particular page.

Sidecar format (same name as image, .json extension):
  [
    {"x": 50, "y": 30, "w": 200, "h": 80},
    {"x": 300, "y": 120, "w": 180, "h": 60}
  ]

If no sidecar exists, returns an empty list (page is skipped gracefully).
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from PIL import Image

from core.interfaces import BaseBubbleDetector, BoundingBox

logger = logging.getLogger(__name__)


class ManualDetector(BaseBubbleDetector):
    """
    Reads bubble coordinates from a JSON file sitting next to the image.
    Useful for:
      - Pages where OpenCV fails
      - Building a ground-truth dataset to train a better detector later
    """

    def __init__(self, **kwargs):
        # Store the last-used image path so detect() can find the sidecar
        self._last_image_path: Path | None = None

    def set_image_path(self, path: str | Path):
        """Called by the pipeline before detect() when using ManualDetector."""
        self._last_image_path = Path(path)

    def detect(self, image: Image.Image) -> list[BoundingBox]:
        if self._last_image_path is None:
            logger.warning("[Manual] No image path set — returning empty list")
            return []

        sidecar = self._last_image_path.with_suffix(".json")
        if not sidecar.exists():
            logger.warning(f"[Manual] No sidecar found at {sidecar}")
            return []

        with open(sidecar) as f:
            data = json.load(f)

        boxes = [BoundingBox(x=r["x"], y=r["y"], w=r["w"], h=r["h"]) for r in data]
        logger.info(f"[Manual] Loaded {len(boxes)} regions from {sidecar.name}")
        return boxes
