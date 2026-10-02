from ats_simulator.parsing.ai_backend import (
    EntityExtractor,
    ExtractedEntities,
    SectionClassifier,
)


class _FakeClassifier:
    def classify(self, line: str) -> str | None:
        return "education" if "school" in line.lower() else None


class _FakeExtractor:
    def extract(self, text: str) -> ExtractedEntities:
        return ExtractedEntities(candidate_name="Test Candidate")


def test_fake_classifier_satisfies_protocol():
    classifier: SectionClassifier = _FakeClassifier()
    assert classifier.classify("High School Diploma") == "education"
    assert classifier.classify("Random prose") is None


def test_fake_extractor_satisfies_protocol():
    extractor: EntityExtractor = _FakeExtractor()
    result = extractor.extract("some text")
    assert result.candidate_name == "Test Candidate"
    assert result.organizations == []
    assert result.date_ranges == []


def test_extracted_entities_defaults():
    entities = ExtractedEntities()
    assert entities.candidate_name is None
    assert entities.organizations == []
    assert entities.date_ranges == []
