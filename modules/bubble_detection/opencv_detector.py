"""
modules/bubble_detection/opencv_detector.py
===========================================
Bubble detector using classic OpenCV computer vision.
No ML model needed — works by finding large white/light contours.

Install:  pip install opencv-python
"""

from __future__ import annotations
import logging
import numpy as np
import cv2
from PIL import Image

from core.interfaces import BaseBubbleDetector, BoundingBox

logger = logging.getLogger(__name__)


class OpenCVDetector(BaseBubbleDetector):
    """
    Strategy:
      1. Convert to greyscale
      2. Threshold to isolate white bubble areas
      3. Find contours
      4. Filter by area + aspect ratio (eliminates panel borders, tiny artifacts)
      5. Return bounding boxes with optional padding

    Config options (detector_options in config.yaml):
      min_area : int — ignore contours smaller than this (default 500 px²)
      padding  : int — extra pixels around each box (default 4)
    """

    def __init__(self, min_area: int = 500, padding: int = 4, **kwargs):
        self.min_area = min_area
        self.padding  = padding

    def detect(self, image: Image.Image) -> list[BoundingBox]:
        # PIL → OpenCV (numpy BGR)
        img_np = np.array(image)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Greyscale + Gaussian blur to reduce noise
        grey = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(grey, (5, 5), 0)

        # Binary threshold — white regions become foreground
        _, binary = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)

        # Find external contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h_img, w_img = grey.shape
        boxes = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(cnt)

            # Filter out the full-page border (> 80% of image size)
            if w > w_img * 0.8 and h > h_img * 0.8:
                continue

            # Filter extreme aspect ratios (likely panel borders)
            aspect = w / max(h, 1)
            if aspect > 8 or aspect < 0.125:
                continue

            # Apply padding (clamped to image bounds)
            x = max(0, x - self.padding)
            y = max(0, y - self.padding)
            w = min(w_img - x, w + self.padding * 2)
            h = min(h_img - y, h + self.padding * 2)

            boxes.append(BoundingBox(x=x, y=y, w=w, h=h))

        logger.debug(f"[OpenCV] {len(boxes)} bubbles after filtering")
        return boxes
