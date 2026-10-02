"""Minimal CV fixture generators for tests — no extra dependencies needed."""
from pathlib import Path

from docx import Document


def _text_stream(items: list[tuple[float, float, str]]) -> bytes:
    content = []
    for x, y, line in items:
        escaped = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        content.append(f"BT /F1 12 Tf {x} {y} Td ({escaped}) Tj ET")
    return "\n".join(content).encode("latin-1")


def _pdf_objects(stream: bytes) -> list[bytes]:
    return [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
    ]


def _write_pdf_stream(path: Path, stream: bytes) -> None:
    objects = _pdf_objects(stream)
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
    _write_pdf_stream(path, _text_stream(items))


def make_pdf_two_column(
    path: Path, left_lines: list[str], right_lines: list[str]
) -> None:
    """Write a minimal two-column PDF: left_lines and right_lines side by side."""
    items = [(72.0, 750.0 - i * 20, line) for i, line in enumerate(left_lines)]
    items += [(320.0, 750.0 - i * 20, line) for i, line in enumerate(right_lines)]
    _write_pdf_stream(path, _text_stream(items))


def make_pdf_with_table(path: Path) -> None:
    """Write a minimal PDF containing an actual ruled 2x2 table (grid lines)."""
    text = _text_stream(
        [
            (80.0, 730.0, "Name"),
            (195.0, 730.0, "Role"),
            (80.0, 680.0, "Mario"),
            (195.0, 680.0, "Dev"),
        ]
    )
    grid = (
        b"72 650 228 100 re S\n"
        b"186 650 m 186 750 l S\n"
        b"72 700 m 300 700 l S"
    )
    _write_pdf_stream(path, text + b"\n" + grid)


def _write_multipage_pdf(path: Path, page_streams: list[bytes]) -> None:
    n_pages = len(page_streams)
    page_obj_nums = [4 + 2 * i for i in range(n_pages)]
    content_obj_nums = [5 + 2 * i for i in range(n_pages)]

    objects: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: f"<< /Type /Pages /Kids [{' '.join(f'{n} 0 R' for n in page_obj_nums)}] "
        f"/Count {n_pages} >>".encode(),
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    for i, stream in enumerate(page_streams):
        objects[page_obj_nums[i]] = (
            f"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 3 0 R >> >> "
            f"/MediaBox [0 0 612 792] /Contents {content_obj_nums[i]} 0 R >>"
        ).encode()
        objects[content_obj_nums[i]] = (
            b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
        )

    pdf = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for num in sorted(objects):
        offsets[num] = len(pdf)
        pdf += f"{num} 0 obj\n".encode() + objects[num] + b"\nendobj\n"

    max_num = max(objects)
    xref_offset = len(pdf)
    pdf += f"xref\n0 {max_num + 1}\n0000000000 65535 f \n".encode()
    for num in range(1, max_num + 1):
        pdf += f"{offsets.get(num, 0):010d} 00000 n \n".encode()
    pdf += (
        f"trailer\n<< /Size {max_num + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF"
    ).encode()

    Path(path).write_bytes(bytes(pdf))


def make_pdf_multipage_mixed_layout(
    path: Path, page1_left: list[str], page1_right: list[str], page2_lines: list[str]
) -> None:
    """Page 1: two columns. Page 2: single column. For per-page isolation tests."""
    items1 = [(72.0, 750.0 - i * 20, line) for i, line in enumerate(page1_left)]
    items1 += [(320.0, 750.0 - i * 20, line) for i, line in enumerate(page1_right)]
    stream1 = _text_stream(items1)
    stream2 = _text_stream(
        [(72.0, 750.0 - i * 20, line) for i, line in enumerate(page2_lines)]
    )
    _write_multipage_pdf(path, [stream1, stream2])


def make_docx(path: Path, lines: list[str]) -> None:
    """Write a minimal DOCX containing the given text lines as paragraphs."""
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    document.save(path)
