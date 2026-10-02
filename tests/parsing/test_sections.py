from ats_simulator.parsing.sections import is_heading, split_into_sections


def test_is_heading_recognizes_known_headings():
    assert is_heading("ESPERIENZA LAVORATIVA") == "experience"
    assert is_heading("Education") == "education"
    assert is_heading("Skills:") == "skills"


def test_is_heading_rejects_prose():
    assert is_heading("Developed a REST API using Python and FastAPI") is None
    assert is_heading("") is None


def test_split_into_sections_clean_cv():
    text = (
        "Mario Rossi\n"
        "mario.rossi@email.com\n"
        "\n"
        "Experience\n"
        "Senior Developer at Acme Corp (2020-2023)\n"
        "Built scalable backend systems\n"
        "\n"
        "Education\n"
        "MSc Computer Science, University of Milan\n"
        "\n"
        "Skills\n"
        "Python, SQL, Docker\n"
    )
    sections = split_into_sections(text)
    assert "Senior Developer at Acme Corp (2020-2023)" in sections["experience"]
    assert "MSc Computer Science, University of Milan" in sections["education"]
    assert "Python, SQL, Docker" in sections["skills"]


def test_split_into_sections_messy_formatting():
    text = (
        "ESPERIENZA LAVORATIVA\n"
        "\n\n\n"
        "- Backend engineer\n"
        "* Led a team of 3\n"
        "\n"
        "COMPETENZE\n"
        "- Python\n"
        "- SQL\n"
    )
    sections = split_into_sections(text)
    assert "- Backend engineer" in sections["experience"]
    assert "* Led a team of 3" in sections["experience"]
    assert "- Python" in sections["skills"]


def test_split_into_sections_no_headings_returns_empty():
    sections = split_into_sections("Just some random text with no headings.")
    assert sections == {}
