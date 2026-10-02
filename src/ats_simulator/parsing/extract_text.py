from pathlib import Path

import pdfplumber
from docx import Document

from .layout import detect_column_gaps, extract_words_with_position, reorder_columns


def extract_text_pdf(path: Path) -> str:
    """Extract raw text from a PDF, reordering multi-column layouts if detected.

    Column detection works on word coordinates across the whole document
    without per-page boundaries — fine for the single-page CVs this targets,
    not verified for multi-page layouts.
    """
    words = extract_words_with_position(path)
    gaps = detect_column_gaps(words)
    if gaps:
        return reorder_columns(words, gaps)
    with pdfplumber.open(path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def extract_text_docx(path: Path) -> str:
    """Extract raw text from a DOCX file, paragraph by paragraph."""
    document = Document(path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def extract_text(path: Path) -> str:
    """Dispatch to the right extractor based on file extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return extract_text_pdf(path)
    if suffix == ".docx":
        return extract_text_docx(path)
    raise ValueError(f"Unsupported file format: {suffix}")
