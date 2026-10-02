import math

from openai import OpenAI

from .sections import looks_like_heading_line

_MODEL = "text-embedding-3-small"
_SIMILARITY_THRESHOLD = 0.5

_PROTOTYPES: dict[str, list[str]] = {
    "summary": ["Professional summary", "Profile", "Career objective"],
    "experience": ["Work experience", "Professional experience", "Employment history"],
    "education": ["Education", "Academic background", "Degrees and qualifications"],
    "skills": ["Skills", "Technical skills", "Core competencies"],
    "languages": ["Languages", "Language skills"],
    "projects": ["Projects", "Key projects", "Technical projects"],
    "certifications": ["Certifications", "Licenses and certifications"],
    "publications": ["Publications"],
    "volunteer": ["Volunteer experience", "Volunteering"],
    "awards": ["Awards", "Honors and awards"],
    "references": ["References"],
    "interests": ["Interests", "Hobbies"],
    "licenses": ["Driving licence", "Driver's license"],
}


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class EmbeddingSectionClassifier:
    """SectionClassifier backed by the OpenAI embeddings API.

    Never raises: any network/API failure makes classify() return None.
    Section classification is an enrichment layered on top of the
    always-available exact-match tier in sections.py, not something the
    rest of the pipeline can depend on being reachable.
    """

    def __init__(self, client: OpenAI | None = None):
        self._client = client or OpenAI()
        self._prototype_embeddings: dict[str, list[list[float]]] | None = None

    def _embed(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=_MODEL, input=texts)
        return [item.embedding for item in response.data]

    def _ensure_prototypes(self) -> None:
        if self._prototype_embeddings is not None:
            return
        phrases = [phrase for phrases in _PROTOTYPES.values() for phrase in phrases]
        embeddings = self._embed(phrases)
        cache: dict[str, list[list[float]]] = {}
        i = 0
        for canonical, category_phrases in _PROTOTYPES.items():
            cache[canonical] = embeddings[i : i + len(category_phrases)]
            i += len(category_phrases)
        self._prototype_embeddings = cache

    def classify(self, line: str) -> str | None:
        if not looks_like_heading_line(line):
            return None
        try:
            self._ensure_prototypes()
            line_embedding = self._embed([line])[0]
        except Exception:
            return None

        best_category, best_score = None, 0.0
        for canonical, prototype_embeddings in self._prototype_embeddings.items():
            for proto_embedding in prototype_embeddings:
                score = _cosine_similarity(line_embedding, proto_embedding)
                if score > best_score:
                    best_category, best_score = canonical, score
        return best_category if best_score >= _SIMILARITY_THRESHOLD else None


def create_default_classifier() -> "EmbeddingSectionClassifier | None":
    """Build the default classifier, or None if no API key is configured.

    Keeps the library fully usable with zero AI setup — callers fall back
    to the always-available exact-match tier in sections.py.
    """
    try:
        return EmbeddingSectionClassifier()
    except Exception:
        return None
