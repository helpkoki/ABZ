"""
core/registry.py
================
Central registry: maps the string names used in config.yaml
to the actual Python classes.

To register a new module:
  1. Write your class (subclass the right ABC in core/interfaces.py)
  2. Add one line to the right dict below
  3. Change config.yaml to point at your new name
  That's it. No other files need touching.
"""

# ── OCR engines ───────────────────────────────────────────────────────────────
from modules.ocr.easyocr_engine   import EasyOCREngine
from modules.ocr.mangaocr_engine  import MangaOCREngine
from modules.ocr.tesseract_engine import TesseractEngine

OCR_REGISTRY: dict = {
    "easyocr":   EasyOCREngine,
    "mangaocr":  MangaOCREngine,
    "tesseract": TesseractEngine,
}

# ── Translation backends ──────────────────────────────────────────────────────
from modules.translation.ollama_translator  import OllamaTranslator
from modules.translation.argos_translator   import ArgosTranslator
from modules.translation.deepl_translator   import DeepLTranslator

TRANSLATOR_REGISTRY: dict = {
    "ollama":  OllamaTranslator,
    "argos":   ArgosTranslator,
    "deepl":   DeepLTranslator,
}

# ── Bubble detectors ──────────────────────────────────────────────────────────
from modules.bubble_detection.opencv_detector import OpenCVDetector
from modules.bubble_detection.manual_detector  import ManualDetector

DETECTOR_REGISTRY: dict = {
    "opencv": OpenCVDetector,
    "manual": ManualDetector,
}

# ── Text overlay renderers ────────────────────────────────────────────────────
from modules.text_overlay.pillow_overlay import PillowOverlay

OVERLAY_REGISTRY: dict = {
    "pillow": PillowOverlay,
}


# ── Factory helper ────────────────────────────────────────────────────────────

def build_from_config(cfg: dict):
    """
    Given the parsed config dict, instantiate and return all four modules.
    Called once at startup from main.py.
    """
    def _get(registry, key, section):
        cls = registry.get(key)
        if cls is None:
            available = list(registry.keys())
            raise ValueError(f"Unknown {section} '{key}'. Available: {available}")
        return cls

    DetectorCls   = _get(DETECTOR_REGISTRY,   cfg["modules"]["bubble_detector"],   "bubble_detector")
    OCRCls        = _get(OCR_REGISTRY,         cfg["modules"]["ocr"],               "ocr")
    TranslatorCls = _get(TRANSLATOR_REGISTRY,  cfg["modules"]["translator"],        "translator")
    OverlayCls    = _get(OVERLAY_REGISTRY,     cfg["modules"]["text_overlay"],      "text_overlay")

    detector   = DetectorCls(**cfg.get("detector_options",   {}))
    ocr        = OCRCls(**cfg.get("ocr_options",             {}))
    translator = TranslatorCls(**cfg.get("translator_options", {}))
    overlay    = OverlayCls(**cfg.get("overlay_options",     {}))

    return detector, ocr, translator, overlay
