"""
modules/ocr/easyocr_engine.py
=============================
OCR module using EasyOCR — good for Indonesian, English, and many other languages.
Best default choice if your manga is NOT Japanese.

Install:  pip install easyocr
"""

from __future__ import annotations
import logging
from PIL import Image
import numpy as np

from core.interfaces import BaseOCR

logger = logging.getLogger(__name__)


class EasyOCREngine(BaseOCR):
    """
    Wraps EasyOCR. Lazy-loads the model on first use so startup is fast.

    Config options (translator_options in config.yaml):
      languages : list of ISO codes, e.g. ["id", "en"]
      gpu       : bool — use CUDA if available
    """

    def __init__(self, languages: list[str] = None, gpu: bool = False):
        self.languages = languages or ["id", "en"]
        self.gpu = gpu
        self._reader = None   # lazy init

    def _get_reader(self):
        if self._reader is None:
            import easyocr
            logger.info(f"[EasyOCR] Loading model for languages: {self.languages}")
            self._reader = easyocr.Reader(self.languages, gpu=self.gpu)
        return self._reader

    def read(self, region: Image.Image) -> tuple[str, float]:
        reader = self._get_reader()

        # EasyOCR expects a numpy array (BGR or RGB — it handles both)
        arr = np.array(region)
        results = reader.readtext(arr)

        if not results:
            return "", 0.0

        # results = list of (bbox, text, confidence)
        # Join all text blocks in reading order (top → bottom)
        results_sorted = sorted(results, key=lambda r: r[0][0][1])  # sort by top-y
        full_text  = " ".join(r[1] for r in results_sorted).strip()
        avg_conf   = sum(r[2] for r in results_sorted) / len(results_sorted)

        return full_text, avg_conf
