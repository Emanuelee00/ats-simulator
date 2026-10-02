import csv
from pathlib import Path

_TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "data" / "skills_taxonomy.csv"


def load_taxonomy(path: Path = _TAXONOMY_PATH) -> dict[str, str]:
    """Load a synonym (lowercase) -> canonical skill name mapping from CSV."""
    mapping: dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # header row
        for canonical, synonyms in reader:
            mapping[canonical.strip().lower()] = canonical.strip()
            for synonym in synonyms.split(";"):
                if synonym.strip():
                    mapping[synonym.strip().lower()] = canonical.strip()
    return mapping


def split_raw_skills(text: str) -> list[str]:
    """Split free-text skills section content into individual raw tokens."""
    tokens = []
    for line in text.splitlines():
        line = line.lstrip("-*• \t")
        for part in line.replace(";", ",").split(","):
            part = part.strip()
            if part:
                tokens.append(part)
    return tokens


def normalize_skills(raw_skills: list[str], taxonomy: dict[str, str] | None = None) -> list[str]:
    """Map raw skill strings to canonical names, preserving order, deduped."""
    taxonomy = load_taxonomy() if taxonomy is None else taxonomy
    seen: set[str] = set()
    normalized = []
    for raw in raw_skills:
        canonical = taxonomy.get(raw.strip().lower(), raw.strip())
        if canonical not in seen:
            seen.add(canonical)
            normalized.append(canonical)
    return normalized
