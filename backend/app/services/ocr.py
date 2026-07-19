from __future__ import annotations

from PIL import Image
import pytesseract


def read_image(image: Image.Image) -> str:
    """Read an image with OCR, with one intentionally small interface for all callers."""
    text = pytesseract.image_to_string(image)
    if not text.strip():
        raise RuntimeError("OCR could not detect readable text in this image")
    return text.strip()
