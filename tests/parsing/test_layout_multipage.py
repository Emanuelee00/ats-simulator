from ats_simulator.parsing.extract_text import extract_text_pdf
from ats_simulator.parsing.layout import extract_words_with_position, has_multi_column_layout
from tests.fixtures import make_pdf_multipage_mixed_layout


def test_extract_words_with_position_tags_page_number(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf_multipage_mixed_layout(
        pdf_path,
        page1_left=["Experience"],
        page1_right=["Skills"],
        page2_lines=["Education"],
    )
    words = extract_words_with_position(pdf_path)
    pages = {w.page_number for w in words}
    assert pages == {0, 1}


def test_has_multi_column_layout_detects_mixed_pages(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf_multipage_mixed_layout(
        pdf_path,
        page1_left=["Experience", "Senior Developer"],
        page1_right=["Skills", "Python"],
        page2_lines=["Education", "MSc Computer Science"],
    )
    # Page 1 has columns, page 2 doesn't — overall this IS a multi-column CV.
    assert has_multi_column_layout(pdf_path) is True


def test_extract_text_pdf_per_page_no_cross_page_interference(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf_multipage_mixed_layout(
        pdf_path,
        page1_left=["Experience", "Senior Developer at Acme"],
        page1_right=["Skills", "Python"],
        page2_lines=["Education", "MSc Computer Science"],
    )
    text = extract_text_pdf(pdf_path)

    # Page 1 columns correctly separated (not interleaved).
    assert "Experience\nSenior Developer at Acme" in text
    assert "Skills\nPython" in text
    # Page 2's single-column content must stay intact and NOT be merged
    # with page 1's columns (the bug this fase fixes: word coordinates
    # pooled across the whole document could previously cause this).
    assert "Education\nMSc Computer Science" in text
    assert "Python" not in text.split("Education")[1]
