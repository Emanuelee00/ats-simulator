from ats_simulator.parsing.sections import is_heading, split_into_sections


class _FakeClassifier:
    """Simulates an AI classifier recognizing headings no exact-match list has."""

    _KNOWN = {
        "istruzione e formazione": "education",
        "patente di guida": "licenses",
        "technical projects": "projects",
    }

    def classify(self, line: str) -> str | None:
        return self._KNOWN.get(line.strip().lower())


def test_is_heading_falls_back_to_classifier():
    classifier = _FakeClassifier()
    assert is_heading("Istruzione e formazione", classifier) == "education"
    assert is_heading("Patente di guida", classifier) == "licenses"


def test_is_heading_exact_match_wins_without_calling_classifier():
    class _ExplodingClassifier:
        def classify(self, line: str) -> str | None:
            raise AssertionError("should not be called when exact match succeeds")

    assert is_heading("Education", _ExplodingClassifier()) == "education"


def test_is_heading_no_classifier_behaves_like_before():
    assert is_heading("Istruzione e formazione") is None


def test_split_into_sections_uses_classifier_for_europass_heading():
    text = (
        "Esperienza lavorativa\n"
        "Senior Developer at Acme\n"
        "\n"
        "Istruzione e formazione\n"
        "MSc Computer Science, University of Lyon\n"
        "\n"
        "Patente di guida\n"
        "Patente B\n"
    )
    sections = split_into_sections(text, classifier=_FakeClassifier())

    assert "MSc Computer Science, University of Lyon" in sections["education"]
    assert "Patente B" in sections["licenses"]
    # Without the classifier, this content would have leaked into "experience".
    assert "MSc Computer Science" not in sections["experience"]
