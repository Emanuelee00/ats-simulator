"""Minimal CV fixture generators for tests — no extra dependencies needed."""
from pathlib import Path

from docx import Document


def _pdf_objects(lines: list[str]) -> list[bytes]:
    content = []
    y = 750
    for line in lines:
        escaped = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        content.append(f"BT /F1 12 Tf 72 {y} Td ({escaped}) Tj ET")
        y -= 20
    stream = "\n".join(content).encode("latin-1")

    return [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
    ]


def make_pdf(path: Path, lines: list[str]) -> None:
    """Write a minimal valid single-page PDF containing the given text lines."""
    objects = _pdf_objects(lines)
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"

    xref_offset = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode()
    pdf += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    ).encode()

    Path(path).write_bytes(bytes(pdf))


def make_docx(path: Path, lines: list[str]) -> None:
    """Write a minimal DOCX containing the given text lines as paragraphs."""
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    document.save(path)
