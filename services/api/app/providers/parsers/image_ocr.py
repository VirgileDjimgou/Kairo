from __future__ import annotations

from io import BytesIO


def parse_image_bytes(file_bytes: bytes) -> str:
    """Extract text from an image using OCR."""
    from PIL import Image, ImageOps
    import pytesseract

    image = Image.open(BytesIO(file_bytes))
    image = ImageOps.exif_transpose(image)
    image = image.convert("L")
    text = pytesseract.image_to_string(image, config="--psm 6")
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("No text content extracted from image")
    return cleaned

