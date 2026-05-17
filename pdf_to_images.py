"""
pdf_to_images.py
================
Converts each PDF page to a PNG image in the input/ folder.

Usage:
    python pdf_to_images.py mychapter.pdf

Install:
    pip install pymupdf
"""

import sys
import fitz  # pymupdf
from pathlib import Path

def pdf_to_images(pdf_path: str, output_dir: str = "input", dpi: int = 150):
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    doc = fitz.open(str(pdf_path))
    saved = []

    for i, page in enumerate(doc):
        mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72 is base DPI
        pix = page.get_pixmap(matrix=mat)
        out_path = output_dir / f"page{i+1:03d}.png"
        pix.save(str(out_path))
        print(f"  Saved: {out_path}")
        saved.append(out_path)

    print(f"\nDone — {len(saved)} page(s) extracted to {output_dir}/")
    return saved

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_images.py chapter.pdf")
        sys.exit(1)
    pdf_to_images(sys.argv[1])