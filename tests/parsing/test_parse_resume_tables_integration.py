from ats_simulator.parsing import parse_resume
from tests.fixtures import make_pdf_with_table


def test_parse_resume_detects_tables(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf_with_table(pdf_path)

    resume = parse_resume(pdf_path)

    assert resume.has_tables is True
