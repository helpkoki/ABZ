# Manga Translator

Local, fully offline manga translation pipeline.  
No API keys. No internet. Runs on your PC.

---

## Project Structure

```
manga_translator/
│
├── main.py                    ← Entry point — run this
├── requirements.txt
│
├── config/
│   └── config.yaml            ← THE FILE YOU EDIT to swap modules
│
├── core/
│   ├── interfaces.py          ← Abstract base classes (the "contracts")
│   ├── pipeline.py            ← Orchestrates the 4 steps in order
│   └── registry.py            ← Maps config names → Python classes
│
├── modules/
│   ├── ocr/
│   │   ├── easyocr_engine.py  ← Good for Indonesian/English (default)
│   │   ├── mangaocr_engine.py ← Best for Japanese
│   │   └── tesseract_engine.py
│   │
│   ├── translation/
│   │   ├── ollama_translator.py  ← Uses your local llama3.2 (default)
│   │   ├── argos_translator.py   ← Fully offline alternative
│   │   └── deepl_translator.py   ← Cloud, needs free API key
│   │
│   ├── bubble_detection/
│   │   ├── opencv_detector.py    ← Auto-detects white bubble regions
│   │   └── manual_detector.py    ← You define regions in a .json file
│   │
│   └── text_overlay/
│       └── pillow_overlay.py     ← Whites out + redraws English text
│
├── input/                     ← Drop your manga pages here
└── output/                    ← Translated pages saved here
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure Ollama is running with llama3.2
ollama serve
ollama pull llama3.2

# 3. Translate a single page
python main.py input/page01.png

# 4. Translate all pages in input/ folder
python main.py --batch
```

---

## How to Swap a Module

Open `config/config.yaml` and change one line:

```yaml
modules:
  ocr: easyocr       # ← change to: mangaocr  or  tesseract
  translator: ollama # ← change to: argos      or  deepl
  bubble_detector: opencv  # ← change to: manual
  text_overlay: pillow     # (only one option for now)
```

That's it. No code changes.

---

## How to Add a Brand New Module

Say you want to add Google Translate as a translator:

**Step 1** — Create the file:
```
modules/translation/google_translator.py
```

**Step 2** — Subclass `BaseTranslator`:
```python
from core.interfaces import BaseTranslator

class GoogleTranslator(BaseTranslator):
    def translate(self, text, source_lang, target_lang) -> str:
        # your code here
        ...
```

**Step 3** — Register it in `core/registry.py`:
```python
from modules.translation.google_translator import GoogleTranslator

TRANSLATOR_REGISTRY = {
    "ollama":  OllamaTranslator,
    "argos":   ArgosTranslator,
    "deepl":   DeepLTranslator,
    "google":  GoogleTranslator,   # ← add this line
}
```

**Step 4** — Switch to it in `config.yaml`:
```yaml
modules:
  translator: google
```

Done. The pipeline picks it up automatically.

---

## Pipeline Steps

```
Image
  │
  ▼
[1] BubbleDetector   — finds white speech bubble regions → list of bounding boxes
  │
  ▼
[2] OCR              — reads text from each cropped region → raw strings
  │
  ▼
[3] Translator       — converts each string to English → translated strings
  │
  ▼
[4] TextOverlay      — whites out originals, draws English text → output image
```

Each step is independent. You can improve any one of them without touching the others.

---

## Tips

- **Bad OCR results?** Try switching `ocr: mangaocr` for Japanese, or lower the EasyOCR threshold
- **Ollama too slow?** Try `argos` as translator — it's faster but less accurate  
- **OpenCV missing bubbles?** Lower `min_area` in `detector_options`, or switch to `manual` and define boxes in a `.json` sidecar file
- **Text overflowing bubbles?** Lower `font_size` in `overlay_options`
