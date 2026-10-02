from ats_simulator.parsing.layout import (
    detect_column_gaps,
    extract_words_with_position,
    reorder_columns,
)
from tests.fixtures import make_pdf, make_pdf_two_column


def test_extract_words_with_position(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(pdf_path, ["Mario Rossi"])
    words = extract_words_with_position(pdf_path)
    texts = [w.text for w in words]
    assert texts == ["Mario", "Rossi"]
    assert words[0].x0 < words[1].x0
    assert all(w.top >= 0 for w in words)


def test_detect_column_gaps_two_column_layout(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf_two_column(
        pdf_path,
        left_lines=["Experience", "Senior Developer"],
        right_lines=["Skills", "Python"],
    )
    words = extract_words_with_position(pdf_path)
    gaps = detect_column_gaps(words)
    assert len(gaps) == 1
    assert 130 < gaps[0] < 320


def test_detect_column_gaps_single_column_no_false_positive(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(
        pdf_path,
        ["Mario Rossi", "Experience", "Senior Developer at Acme Corp", "Skills"],
    )
    words = extract_words_with_position(pdf_path)
    assert detect_column_gaps(words) == []


def test_reorder_columns_keeps_columns_separate(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf_two_column(
        pdf_path,
        left_lines=["Experience", "Senior Developer"],
        right_lines=["Skills", "Python"],
    )
    words = extract_words_with_position(pdf_path)
    gaps = detect_column_gaps(words)
    text = reorder_columns(words, gaps)

    # Left column fully precedes right column, not interleaved line-by-line
    # the way naive left-to-right reading order would mix them.
    assert text == "Experience\nSenior Developer\nSkills\nPython"
