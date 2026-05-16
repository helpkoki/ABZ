"""
modules/ocr/mangaocr_engine.py
==============================
OCR module using manga-ocr — purpose-built for Japanese manga fonts.
Significantly more accurate than generic OCR for Japanese text.

Install:  pip install manga-ocr
"""

from __future__ import annotations
import logging
from PIL import Image

from core.interfaces import BaseOCR

logger = logging.getLogger(__name__)


class MangaOCREngine(BaseOCR):
    """
    Wraps the manga-ocr library.
    Only reads Japanese — pair with a translator that handles Japanese source.
    Model downloads automatically on first use (~400 MB).
    """

    def __init__(self, **kwargs):
        self._ocr = None   # lazy init

    def _get_ocr(self):
        if self._ocr is None:
            from manga_ocr import MangaOcr
            logger.info("[MangaOCR] Loading model (first run downloads ~400 MB)...")
            self._ocr = MangaOcr()
        return self._ocr

    def read(self, region: Image.Image) -> tuple[str, float]:
        ocr = self._get_ocr()
        text = ocr(region)
        # manga-ocr doesn't return a confidence score; we return 1.0 as a placeholder
        return text.strip(), 1.0
