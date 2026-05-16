"""
core/pipeline.py
================
The pipeline is the ONLY place that calls modules.
It doesn't know (or care) which concrete implementation is running —
it just calls the ABC methods in order.

Flow:
  image  →  BubbleDetector  →  OCR  →  Translator  →  TextOverlay  →  output image
"""

import logging
from pathlib import Path
from PIL import Image

from core.interfaces import (
    BaseBubbleDetector,
    BaseOCR,
    BaseTranslator,
    BaseTextOverlay,
    TextRegion,
)

logger = logging.getLogger(__name__)


class TranslationPipeline:
    def __init__(
        self,
        detector: BaseBubbleDetector,
        ocr: BaseOCR,
        translator: BaseTranslator,
        overlay: BaseTextOverlay,
        source_lang: str = "auto",
        target_lang: str = "en",
    ):
        # All four slots accept any object that satisfies the ABC.
        # To swap a module: just pass a different object here.
        self.detector   = detector
        self.ocr        = ocr
        self.translator = translator
        self.overlay    = overlay
        self.source_lang = source_lang
        self.target_lang = target_lang

    # ── Main entry point ──────────────────────────────────────────────────────

    def run(self, image_path: str | Path) -> Image.Image:
        """
        Full pipeline: file path  →  translated PIL image.
        """
        image_path = Path(image_path)
        logger.info(f"[Pipeline] Loading image: {image_path}")
        image = Image.open(image_path).convert("RGB")

        # Step 1 — detect bubble regions
        logger.info("[Pipeline] Step 1/4 — Bubble detection")
        bboxes = self.detector.detect(image)
        logger.info(f"[Pipeline]   → {len(bboxes)} region(s) found")

        # Step 2 — OCR each region
        logger.info("[Pipeline] Step 2/4 — OCR")
        regions = []
        for bbox in bboxes:
            crop = image.crop((bbox.x, bbox.y, bbox.x + bbox.w, bbox.y + bbox.h))
            text, confidence = self.ocr.read(crop)
            if text.strip():
                regions.append(TextRegion(bbox=bbox, original_text=text, confidence=confidence))
                logger.debug(f"  OCR [{confidence:.2f}]: {text!r}")

        logger.info(f"[Pipeline]   → {len(regions)} non-empty region(s)")

        # Step 3 — translate
        logger.info("[Pipeline] Step 3/4 — Translation")
        for region in regions:
            region.translated_text = self.translator.translate(
                region.original_text, self.source_lang, self.target_lang
            )
            logger.debug(f"  {region.original_text!r}  →  {region.translated_text!r}")

        # Step 4 — render overlay
        logger.info("[Pipeline] Step 4/4 — Text overlay")
        result = self.overlay.apply(image, regions)

        logger.info("[Pipeline] Done ✓")
        return result

    # ── Convenience: process a whole folder ──────────────────────────────────

    def run_batch(self, input_dir: str | Path, output_dir: str | Path) -> list[Path]:
        input_dir  = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        exts = {".jpg", ".jpeg", ".png", ".webp"}
        pages = sorted(p for p in input_dir.iterdir() if p.suffix.lower() in exts)
        outputs = []

        for page in pages:
            logger.info(f"[Batch] Processing {page.name}")
            result = self.run(page)
            out_path = output_dir / page.name
            result.save(out_path)
            outputs.append(out_path)
            logger.info(f"[Batch] Saved → {out_path}")

        return outputs
