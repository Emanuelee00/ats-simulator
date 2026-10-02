import pytest

from ats_simulator.parsing.extract_text import (
    extract_text,
    extract_text_docx,
    extract_text_pdf,
)
from tests.fixtures import make_docx, make_pdf


def test_extract_text_pdf(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(pdf_path, ["Mario Rossi", "mario.rossi@email.com"])
    text = extract_text_pdf(pdf_path)
    assert "mario.rossi@email.com" in text


def test_extract_text_docx(tmp_path):
    docx_path = tmp_path / "cv.docx"
    make_docx(docx_path, ["Mario Rossi", "mario.rossi@email.com"])
    text = extract_text_docx(docx_path)
    assert "mario.rossi@email.com" in text


def test_extract_text_dispatcher_pdf(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(pdf_path, ["hello@example.com"])
    assert "hello@example.com" in extract_text(pdf_path)


def test_extract_text_dispatcher_docx(tmp_path):
    docx_path = tmp_path / "cv.docx"
    make_docx(docx_path, ["hello@example.com"])
    assert "hello@example.com" in extract_text(docx_path)


def test_extract_text_unsupported_format(tmp_path):
    txt_path = tmp_path / "cv.txt"
    txt_path.write_text("hello")
    with pytest.raises(ValueError):
        extract_text(txt_path)
