from ats_simulator.parsing.embedding_classifier import (
    EmbeddingSectionClassifier,
    _cosine_similarity,
)


class _FakeEmbeddingItem:
    def __init__(self, embedding):
        self.embedding = embedding


class _FakeEmbeddingResponse:
    def __init__(self, embeddings):
        self.data = [_FakeEmbeddingItem(e) for e in embeddings]


class _FakeEmbeddings:
    def __init__(self, embedding_fn):
        self._embedding_fn = embedding_fn
        self.call_count = 0

    def create(self, model, input):
        self.call_count += 1
        return _FakeEmbeddingResponse([self._embedding_fn(text) for text in input])


class _FakeClient:
    def __init__(self, embedding_fn):
        self.embeddings = _FakeEmbeddings(embedding_fn)


class _FailingEmbeddings:
    def create(self, model, input):
        raise RuntimeError("simulated network error")


class _FailingClient:
    def __init__(self):
        self.embeddings = _FailingEmbeddings()


def _toy_embedding(text: str) -> list[float]:
    """Deterministic toy embedding so similarity behaves predictably in tests."""
    lowered = text.lower()
    if any(w in lowered for w in ("education", "academic", "degrees", "istruzione", "formazione")):
        return [1.0, 0.0, 0.0]
    if any(w in lowered for w in ("work", "experience", "employment")):
        return [0.0, 1.0, 0.0]
    return [0.0, 0.0, 1.0]


def test_cosine_similarity_identical_vectors():
    assert _cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0


def test_cosine_similarity_orthogonal_vectors():
    assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_classify_skips_api_call_for_prose():
    client = _FakeClient(_toy_embedding)
    classifier = EmbeddingSectionClassifier(client=client)

    result = classifier.classify(
        "Developed skills in project management for a team of 5 engineers."
    )

    assert result is None
    assert client.embeddings.call_count == 0


def test_classify_picks_closest_category_across_languages():
    client = _FakeClient(_toy_embedding)
    classifier = EmbeddingSectionClassifier(client=client)

    assert classifier.classify("Istruzione e formazione") == "education"


def test_classify_returns_none_on_api_failure():
    classifier = EmbeddingSectionClassifier(client=_FailingClient())

    assert classifier.classify("Istruzione e formazione") is None


def test_classify_caches_prototype_embeddings_across_calls():
    client = _FakeClient(_toy_embedding)
    classifier = EmbeddingSectionClassifier(client=client)

    classifier.classify("Education")
    calls_after_first = client.embeddings.call_count
    classifier.classify("Work experience")

    # Second call should only embed the new line, not re-embed all prototypes.
    assert client.embeddings.call_count == calls_after_first + 1
