from pathlib import Path

import pdfplumber
from docx import Document

from .layout import detect_column_gaps, extract_words_with_position, reorder_columns


def extract_text_pdf(path: Path) -> str:
    """Extract raw text from a PDF, reordering multi-column layouts per page.

    Column detection and reordering run independently per page — fixes a
    previously documented bug where word coordinates were pooled across
    the whole document, risking cross-page interference on multi-page CVs.
    """
    words = extract_words_with_position(path)
    with pdfplumber.open(path) as pdf:
        plain_pages = [page.extract_text() or "" for page in pdf.pages]

    page_texts = []
    for page_number, plain_text in enumerate(plain_pages):
        page_words = [w for w in words if w.page_number == page_number]
        gaps = detect_column_gaps(page_words)
        page_texts.append(reorder_columns(page_words, gaps) if gaps else plain_text)
    return "\n".join(page_texts)


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


def is_text_sparse(text: str, min_words: int = 30) -> bool:
    """Flag text too short to be a real CV — usually an image-based/scanned PDF.

    Most real ATS parsers cannot read text from scanned or image-only
    documents at all: this is the single most common cause of a CV being
    completely invisible to an ATS, more severe than any formatting issue.
    """
    return len(text.split()) < min_words
