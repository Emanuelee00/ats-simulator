from ats_simulator.parsing import parse_resume
from tests.fixtures import make_pdf


def test_parse_resume_end_to_end(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(
        pdf_path,
        [
            "Mario Rossi",
            "mario.rossi@email.com +39 333 1234567",
            "Experience",
            "Senior Developer at Acme Corp",
            "Skills",
            "Python, SQL",
        ],
    )

    resume = parse_resume(pdf_path)

    assert resume.contact.email == "mario.rossi@email.com"
    section_names = {s.name for s in resume.sections}
    assert "experience" in section_names
    assert "skills" in section_names
