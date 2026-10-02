from pathlib import Path

import pdfplumber


def has_pdf_tables(path: Path) -> bool:
    """Detect genuine ruled table structures in a PDF (DOCX: always False).

    Distinct from the multi-column layout heuristic in layout.py: this finds
    actual table grids (pdfplumber's line-based table detection), a known
    harder case for ATS parsers since cell reading order can get scrambled
    in ways a simple column-gap heuristic wouldn't catch.
    """
    if Path(path).suffix.lower() != ".pdf":
        return False
    with pdfplumber.open(path) as pdf:
        return any(page.extract_tables() for page in pdf.pages)
