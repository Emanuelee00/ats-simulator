from ats_simulator.parsing import parse_resume
from tests.fixtures import make_pdf


def test_parse_resume_computes_experience_years_and_gap(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(
        pdf_path,
        [
            "Mario Rossi",
            "Experience",
            "Gen 2018 - Giu 2019 Junior Developer",
            "Gen 2021 - Dic 2022 Senior Developer",
        ],
    )

    resume = parse_resume(pdf_path)

    assert resume.total_experience_years is not None
    assert resume.total_experience_years > 2.0
    assert len(resume.employment_gaps) == 1


def test_parse_resume_no_dates_found_gives_none_and_no_gaps(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(pdf_path, ["Mario Rossi", "Experience", "Senior Developer at Acme"])

    resume = parse_resume(pdf_path)

    assert resume.total_experience_years is None
    assert resume.employment_gaps == []
