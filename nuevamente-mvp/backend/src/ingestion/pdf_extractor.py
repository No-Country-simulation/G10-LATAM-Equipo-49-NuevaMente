import fitz  # PyMuPDF
from src.core.exceptions import ScannedPdfError


def extract_pdf(data: bytes) -> list[dict]:
    document = fitz.open(stream=data, filetype="pdf")
    pages = []
    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()
        pages.append({"page": page_number, "text": text})
    return pages


def extract_pdf_text(data: bytes) -> tuple[str, list[dict]]:
    pages = extract_pdf(data)
    raw_text = "\n\n".join(p["text"] for p in pages if p["text"])
    if not raw_text.strip():
        raise ScannedPdfError(
            "El PDF no contiene texto extraíble (posible documento escaneado). "
            "OCR no está habilitado en el MVP."
        )
    return raw_text, pages
