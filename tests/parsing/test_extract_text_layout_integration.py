from ats_simulator.parsing import parse_resume
from ats_simulator.parsing.extract_text import extract_text_pdf
from tests.fixtures import make_pdf_two_column


def test_extract_text_pdf_reorders_two_column_layout(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf_two_column(
        pdf_path,
        left_lines=["Experience", "Senior Developer"],
        right_lines=["Skills", "Python"],
    )
    text = extract_text_pdf(pdf_path)
    assert text == "Experience\nSenior Developer\nSkills\nPython"


def test_parse_resume_two_column_sections_not_mixed(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf_two_column(
        pdf_path,
        left_lines=["Experience", "Senior Developer at Acme"],
        right_lines=["Skills", "Python"],
    )
    resume = parse_resume(pdf_path)
    sections = {s.name: s.content for s in resume.sections}
    assert "Senior Developer at Acme" in sections["experience"]
    assert "Python" in sections["skills"]
    # Before layout-aware reordering, naive reading order would have
    # interleaved "Senior Developer at Acme" and "Skills"/"Python" on the
    # same text line, breaking section assignment.
    assert "Python" not in sections["experience"]
