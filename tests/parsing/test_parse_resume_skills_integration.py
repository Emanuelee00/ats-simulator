from ats_simulator.parsing import parse_resume
from tests.fixtures import make_pdf


def test_parse_resume_normalizes_skills_section(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(
        pdf_path,
        [
            "Mario Rossi",
            "Skills",
            "ML, py, Docker",
        ],
    )

    resume = parse_resume(pdf_path)

    assert resume.skills == ["Machine Learning", "Python", "Docker"]


def test_parse_resume_no_skills_section_gives_empty_list(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(pdf_path, ["Mario Rossi", "Experience", "Senior Developer"])

    resume = parse_resume(pdf_path)

    assert resume.skills == []
