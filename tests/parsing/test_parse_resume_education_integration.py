from ats_simulator.parsing import parse_resume
from tests.fixtures import make_pdf


def test_parse_resume_normalizes_education_level(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(
        pdf_path,
        ["Mario Rossi", "Education", "Laurea Magistrale in Ingegneria Informatica"],
    )

    resume = parse_resume(pdf_path)

    assert resume.education_level == "Master's Degree"
