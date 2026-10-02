from ats_simulator.parsing.sections import (
    is_heading,
    looks_like_heading_line,
    split_into_sections,
)


def test_looks_like_heading_line_accepts_short_headings():
    assert looks_like_heading_line("Istruzione e formazione") is True
    assert looks_like_heading_line("Patente di guida") is True
    assert looks_like_heading_line("Hobby e interessi") is True


def test_looks_like_heading_line_rejects_prose():
    long_sentence = "Developed skills in project management for a team of 5 engineers."
    assert looks_like_heading_line(long_sentence) is False
    assert looks_like_heading_line("") is False


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


def test_is_heading_recognizes_extended_categories():
    assert is_heading("Professional Summary") == "summary"
    assert is_heading("Profilo professionale") == "summary"
    assert is_heading("Languages") == "languages"
    assert is_heading("Lingue") == "languages"
    assert is_heading("Publications") == "publications"
    assert is_heading("Volontariato") == "volunteer"
    assert is_heading("Awards") == "awards"
    assert is_heading("References") == "references"
    assert is_heading("Hobbies") == "interests"


def test_split_into_sections_keeps_extended_sections_separate():
    text = (
        "Summary\n"
        "Backend engineer with 5 years of experience\n"
        "\n"
        "Experience\n"
        "Senior Developer at Acme Corp\n"
        "\n"
        "Languages\n"
        "English (fluent), Italian (native)\n"
    )
    sections = split_into_sections(text)
    assert "Backend engineer with 5 years of experience" in sections["summary"]
    assert "Senior Developer at Acme Corp" in sections["experience"]
    assert "English (fluent), Italian (native)" in sections["languages"]
    # Without the "Languages" heading recognized, this content would have
    # leaked into the "experience" section instead of being isolated.
    assert "English (fluent)" not in sections["experience"]
