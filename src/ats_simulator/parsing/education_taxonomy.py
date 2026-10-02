import csv
from pathlib import Path

_TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "data" / "education_levels.csv"


def load_education_taxonomy(path: Path = _TAXONOMY_PATH) -> list[tuple[str, str]]:
    """Load (synonym, canonical) pairs, longest synonym first for safe matching.

    Longest-first avoids a short generic synonym ("laurea") shadowing a more
    specific one that contains it ("laurea magistrale") when scanning free text.
    """
    pairs = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # header row
        for canonical, synonyms in reader:
            pairs.append((canonical.strip().lower(), canonical.strip()))
            for synonym in synonyms.split(";"):
                if synonym.strip():
                    pairs.append((synonym.strip().lower(), canonical.strip()))
    return sorted(pairs, key=lambda pair: len(pair[0]), reverse=True)


def normalize_education_level(text: str, taxonomy: list[tuple[str, str]] | None = None) -> str | None:
    """Find a recognized education level mentioned in free text, if any."""
    taxonomy = load_education_taxonomy() if taxonomy is None else taxonomy
    lowered = text.lower()
    for synonym, canonical in taxonomy:
        if synonym in lowered:
            return canonical
    return None
