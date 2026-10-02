"""Minimal CV fixture generators for tests — no extra dependencies needed."""
from pathlib import Path

from docx import Document


def _pdf_objects(items: list[tuple[float, float, str]]) -> list[bytes]:
    content = []
    for x, y, line in items:
        escaped = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        content.append(f"BT /F1 12 Tf {x} {y} Td ({escaped}) Tj ET")
    stream = "\n".join(content).encode("latin-1")

    return [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
    ]


def _write_pdf(path: Path, items: list[tuple[float, float, str]]) -> None:
    objects = _pdf_objects(items)
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


def make_pdf(path: Path, lines: list[str]) -> None:
    """Write a minimal valid single-page, single-column PDF from text lines."""
    items = [(72.0, 750.0 - i * 20, line) for i, line in enumerate(lines)]
    _write_pdf(path, items)


def make_pdf_two_column(
    path: Path, left_lines: list[str], right_lines: list[str]
) -> None:
    """Write a minimal two-column PDF: left_lines and right_lines side by side."""
    items = [(72.0, 750.0 - i * 20, line) for i, line in enumerate(left_lines)]
    items += [(320.0, 750.0 - i * 20, line) for i, line in enumerate(right_lines)]
    _write_pdf(path, items)


def make_docx(path: Path, lines: list[str]) -> None:
    """Write a minimal DOCX containing the given text lines as paragraphs."""
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    document.save(path)
