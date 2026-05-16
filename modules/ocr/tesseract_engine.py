"""
modules/ocr/tesseract_engine.py
================================
OCR module using Tesseract — the classic open-source OCR engine.
Decent for printed text but weaker than EasyOCR on manga fonts.

Install:
  sudo apt install tesseract-ocr          # Linux
  brew install tesseract                  # macOS
  pip install pytesseract
"""

from __future__ import annotations
import logging
from PIL import Image

from core.interfaces import BaseOCR

logger = logging.getLogger(__name__)


class TesseractEngine(BaseOCR):
    """
    Wraps pytesseract.

    Config options:
      lang : Tesseract language string e.g. "eng+ind+jpn"
    """

    def __init__(self, lang: str = "eng+ind", **kwargs):
        self.lang = lang

    def read(self, region: Image.Image) -> tuple[str, float]:
        import pytesseract

        # Get full output with confidence
        data = pytesseract.image_to_data(
            region,
            lang=self.lang,
            output_type=pytesseract.Output.DICT
        )

        words = []
        confs = []
        for text, conf in zip(data["text"], data["conf"]):
            text = text.strip()
            if text and int(conf) > 0:
                words.append(text)
                confs.append(int(conf) / 100.0)

        if not words:
            return "", 0.0

        full_text = " ".join(words)
        avg_conf  = sum(confs) / len(confs)
        return full_text, avg_conf
