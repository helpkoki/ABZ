"""
main.py
=======
Entry point. Reads config.yaml, builds the pipeline, runs it.

Usage:
  # Translate a single image
  python main.py image.png

  # Translate all images in input/ folder
  python main.py --batch

  # Use a different config file
  python main.py image.png --config config/my_other_config.yaml
"""

import argparse
import logging
import sys
from pathlib import Path

import yaml

from core.pipeline  import TranslationPipeline
from core.registry  import build_from_config


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Manga Translator")
    parser.add_argument("image",   nargs="?",  help="Path to a single manga image")
    parser.add_argument("--batch", action="store_true", help="Process all images in input_dir")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config YAML")
    args = parser.parse_args()

    cfg = load_config(args.config)
    setup_logging(cfg.get("logging", {}).get("level", "INFO"))
    logger = logging.getLogger(__name__)

    # Build all four modules from config
    detector, ocr, translator, overlay = build_from_config(cfg)

    pipeline = TranslationPipeline(
        detector   = detector,
        ocr        = ocr,
        translator = translator,
        overlay    = overlay,
        source_lang = cfg["language"]["source"],
        target_lang = cfg["language"]["target"],
    )

    output_dir = Path(cfg["paths"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.batch:
        input_dir = Path(cfg["paths"]["input_dir"])
        results = pipeline.run_batch(input_dir, output_dir)
        logger.info(f"Batch done — {len(results)} page(s) saved to {output_dir}/")

    elif args.image:
        img_path = Path(args.image)
        if not img_path.exists():
            logger.error(f"File not found: {img_path}")
            sys.exit(1)

        result = pipeline.run(img_path)
        out_path = output_dir / img_path.name
        result.save(out_path)
        logger.info(f"Saved → {out_path}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
