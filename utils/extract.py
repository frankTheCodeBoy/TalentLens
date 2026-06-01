import fitz  # PyMuPDF
import pytesseract
from PIL import Image


def extract_text_pdf(path: str) -> str:
    doc = fitz.open(path)
    text = ""
    for page in doc:
        # Try normal text extraction
        page_text = page.get_text("text")
        if not page_text.strip():
            # Fallback: OCR if page is image-only
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img)
        text += page_text + " "
    return text
