from pathlib import Path

import pdfplumber
from docx import Document


def extract_text_pdf(path: Path) -> str:
    """Extract raw text from a PDF file, page by page."""
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
