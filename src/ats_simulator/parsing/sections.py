_SECTION_HEADINGS: dict[str, set[str]] = {
    "experience": {
        "experience",
        "work experience",
        "esperienza",
        "esperienza lavorativa",
        "esperienze professionali",
    },
    "education": {"education", "formazione", "istruzione"},
    "skills": {"skills", "competenze", "competenze tecniche"},
    "projects": {"projects", "progetti"},
    "certifications": {"certifications", "certificazioni"},
}


def is_heading(line: str) -> str | None:
    """Return the canonical section name if the line is a known heading."""
    normalized = line.strip().lower().rstrip(":")
    for canonical, variants in _SECTION_HEADINGS.items():
        if normalized in variants:
            return canonical
    return None


def split_into_sections(text: str) -> dict[str, str]:
    """Split resume text into sections keyed by canonical heading name.

    Lines before the first recognized heading (e.g. name, contact info)
    are not part of any section and are dropped here — they are handled
    separately by contact_fields on the full text.
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        heading = is_heading(line)
        if heading:
            current = heading
            sections.setdefault(current, [])
            continue
        if current is not None and line.strip():
            sections[current].append(line.strip())
    return {name: "\n".join(lines) for name, lines in sections.items()}
