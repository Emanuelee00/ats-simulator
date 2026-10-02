from .ai_backend import SectionClassifier

_SECTION_HEADINGS: dict[str, set[str]] = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "about me",
        "objective",
        "career objective",
        "profilo",
        "profilo professionale",
        "obiettivo",
        "chi sono",
        "sintesi",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "career history",
        "work history",
        "esperienza",
        "esperienza lavorativa",
        "esperienze professionali",
        "carriera professionale",
    },
    "education": {
        "education",
        "formazione",
        "istruzione",
        "titoli di studio",
        "percorso formativo",
    },
    "skills": {
        "skills",
        "technical skills",
        "core competencies",
        "competenze",
        "competenze tecniche",
        "abilità",
    },
    "languages": {
        "languages",
        "language skills",
        "lingue",
        "competenze linguistiche",
    },
    "projects": {"projects", "progetti"},
    "certifications": {"certifications", "certificazioni", "certificati"},
    "publications": {"publications", "pubblicazioni"},
    "volunteer": {
        "volunteer experience",
        "volunteering",
        "volontariato",
        "attività di volontariato",
    },
    "awards": {"awards", "honors", "awards and honors", "premi", "riconoscimenti"},
    "references": {"references", "referenze"},
    "interests": {"interests", "hobbies", "interessi", "hobby"},
}


_MAX_HEADING_LENGTH = 40
_MAX_HEADING_WORDS = 6


def looks_like_heading_line(line: str) -> bool:
    """Cheap shape check: is this line short enough to plausibly be a heading?

    Filters out ordinary prose before any (costly, API-based) semantic
    classification is attempted — a real heading is almost always a short
    standalone line, not a full sentence ending in a period.
    """
    stripped = line.strip().rstrip(":")
    if not stripped or stripped.endswith("."):
        return False
    return len(stripped) <= _MAX_HEADING_LENGTH and len(stripped.split()) <= _MAX_HEADING_WORDS


def is_heading(line: str, classifier: SectionClassifier | None = None) -> str | None:
    """Return the canonical section name if the line is a known heading.

    Tries the exact-match set first (instant, zero risk, no network). Only
    if that fails and a classifier is given does it fall back to semantic
    classification — an enrichment, never a hard dependency.
    """
    normalized = line.strip().lower().rstrip(":")
    for canonical, variants in _SECTION_HEADINGS.items():
        if normalized in variants:
            return canonical
    if classifier is not None:
        return classifier.classify(line)
    return None


def split_into_sections(text: str, classifier: SectionClassifier | None = None) -> dict[str, str]:
    """Split resume text into sections keyed by canonical heading name.

    Lines before the first recognized heading (e.g. name, contact info)
    are not part of any section and are dropped here — they are handled
    separately by contact_fields on the full text.
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        heading = is_heading(line, classifier)
        if heading:
            current = heading
            sections.setdefault(current, [])
            continue
        if current is not None and line.strip():
            sections[current].append(line.strip())
    return {name: "\n".join(lines) for name, lines in sections.items()}
