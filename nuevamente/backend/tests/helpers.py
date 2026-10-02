"""Utilidades de prueba: generación de PDFs sin dependencias externas."""
from io import BytesIO

from pypdf import PdfReader, PdfWriter


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _content_stream(text: str) -> bytes:
    if not text:
        return b""
    lines = ["BT", "/F1 12 Tf", "72 720 Td", "16 TL"]
    lines += [f"({_escape(line)}) Tj T*" for line in text.split("\n")]
    lines.append("ET")
    return "\n".join(lines).encode("latin-1")


def make_pdf(pages: list[str]) -> bytes:
    """Crea un PDF válido con una página por cada texto (`""` = página sin texto)."""
    objs: dict[int, bytes] = {1: b"<< /Type /Catalog /Pages 2 0 R >>"}
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(len(pages)))
    objs[2] = f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode()
    objs[3] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    for i, text in enumerate(pages):
        page_id, content_id = 4 + 2 * i, 5 + 2 * i
        objs[page_id] = (
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>"
        ).encode()
        stream = _content_stream(text)
        objs[content_id] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream"
        )

    out = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for num in sorted(objs):
        offsets[num] = len(out)
        out += f"{num} 0 obj\n".encode() + objs[num] + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n".encode() + b"0000000000 65535 f \n"
    for num in sorted(objs):
        out += f"{offsets[num]:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(out)


def encrypt_pdf(pdf: bytes, password: str = "secreto") -> bytes:
    """Devuelve el PDF protegido con contraseña de apertura."""
    writer = PdfWriter()
    for page in PdfReader(BytesIO(pdf)).pages:
        writer.add_page(page)
    writer.encrypt(password)
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()
