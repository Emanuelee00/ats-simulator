import re

_EMAIL_HINT = re.compile(r"@")
_URL_HINT = re.compile(r"https?://|www\.", re.IGNORECASE)
_DIGIT = re.compile(r"\d")


def extract_candidate_name(text: str) -> str | None:
    """Heuristic: the candidate's name is usually the first substantive line.

    Skips lines that look like contact info (email, URL, mostly digits)
    rather than a name. No NER — a lightweight approximation, not a
    guarantee, but what most real-world parsers also rely on for this field.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _EMAIL_HINT.search(stripped) or _URL_HINT.search(stripped):
            continue
        if len(_DIGIT.findall(stripped)) > 3:
            continue
        return stripped
    return None
