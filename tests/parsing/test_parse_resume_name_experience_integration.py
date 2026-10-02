from ats_simulator.parsing import parse_resume
from tests.fixtures import make_pdf


def test_parse_resume_extracts_name_and_experience_entries(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(
        pdf_path,
        [
            "Mario Rossi",
            "mario.rossi@email.com",
            "Experience",
            "Senior Developer at Acme Corp",
            "Junior Developer presso Beta Srl",
        ],
    )

    resume = parse_resume(pdf_path)

    assert resume.candidate_name == "Mario Rossi"
    assert len(resume.experience_entries) == 2
    assert resume.experience_entries[0].title == "Senior Developer"
    assert resume.experience_entries[0].company == "Acme Corp"
    assert resume.experience_entries[1].company == "Beta Srl"
