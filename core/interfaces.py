"""
core/interfaces.py
==================
Abstract base classes (ABCs) for every swappable module.

Rule: if you want to add a new OCR engine, translation service,
bubble detector, or text renderer — subclass the right ABC here,
implement all abstract methods, and register it in config.yaml.
Nothing else in the codebase needs to change.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from PIL import Image


# ─── Shared data types ────────────────────────────────────────────────────────

@dataclass
class BoundingBox:
    """Pixel coordinates of a detected region."""
    x: int       # left
    y: int       # top
    w: int       # width
    h: int       # height


@dataclass
class TextRegion:
    """One detected text block (bubble, caption, sfx, etc.)."""
    bbox: BoundingBox
    original_text: str
    translated_text: str = ""
    confidence: float = 1.0   # OCR confidence 0-1


# ─── Module ABCs ─────────────────────────────────────────────────────────────

class BaseBubbleDetector(ABC):
    """
    Finds speech-bubble / text regions in a manga page.
    Swap this out for a deep-learning detector when you want better accuracy.
    """

    @abstractmethod
    def detect(self, image: Image.Image) -> List[BoundingBox]:
        """
        Parameters
        ----------
        image : PIL.Image  (RGB)

        Returns
        -------
        List of BoundingBox, one per detected region.
        """
        ...


class BaseOCR(ABC):
    """
    Reads text out of a cropped image region.
    Swap between manga-ocr, EasyOCR, Tesseract, etc.
    """

    @abstractmethod
    def read(self, region: Image.Image) -> tuple[str, float]:
        """
        Parameters
        ----------
        region : PIL.Image  — cropped bubble / text area

        Returns
        -------
        (text: str, confidence: float 0-1)
        """
        ...


class BaseTranslator(ABC):
    """
    Translates a string from source_lang to target_lang.
    Swap between Ollama, DeepL, Google, Argos, etc.
    """

    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Parameters
        ----------
        text        : raw OCR string
        source_lang : ISO 639-1 code e.g. 'ja', 'id', 'auto'
        target_lang : ISO 639-1 code e.g. 'en'

        Returns
        -------
        Translated string.
        """
        ...


class BaseTextOverlay(ABC):
    """
    Whites-out the original text and draws translated text on the image.
    Swap for different font styles or rendering approaches.
    """

    @abstractmethod
    def apply(
        self,
        image: Image.Image,
        regions: List[TextRegion],
    ) -> Image.Image:
        """
        Parameters
        ----------
        image   : PIL.Image  — the full manga page (will NOT be mutated)
        regions : list of TextRegion with translated_text filled in

        Returns
        -------
        New PIL.Image with translations overlaid.
        """
        ...
