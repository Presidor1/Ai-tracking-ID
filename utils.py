import os
from PIL import Image
from PIL.ExifTags import TAGS
import pytesseract
import filetype

def extract_exif(filepath):
    """Extract EXIF metadata from images (camera, GPS if available)."""
    try:
        img = Image.open(filepath)
        exif_data = img._getexif()
        if not exif_data:
            return {}
        return {TAGS.get(tag): val for tag, val in exif_data.items() if tag in TAGS}
    except Exception:
        return {}

def detect_file_type(filepath):
    """Detect MIME type of file (image, video, etc.)."""
    kind = filetype.guess(filepath)
    return kind.mime if kind else "unknown"

def run_ocr(filepath):
    """Run OCR (Optical Character Recognition) on an image."""
    try:
        text = pytesseract.image_to_string(Image.open(filepath))
        return text.strip()
    except Exception:
        return ""
