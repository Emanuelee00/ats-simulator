import re

from pydantic import BaseModel

_SEPARATOR_RE = re.compile(r"\bpresso\b|\bat\b|—|\|| - ", re.IGNORECASE)


class ExperienceEntry(BaseModel):
    raw_line: str
    title: str | None = None
    company: str | None = None


def parse_experience_entry(line: str) -> ExperienceEntry:
    """Split 'Title at/presso Company' into structured fields, best-effort.

    Pure pattern-matching on known separators, not true NER: works for the
    common explicit-separator phrasing, not for free-form entries without one.
    """
    match = _SEPARATOR_RE.search(line)
    if not match:
        return ExperienceEntry(raw_line=line.strip(), title=line.strip() or None)
    title = line[: match.start()].strip() or None
    company = line[match.end() :].strip() or None
    return ExperienceEntry(raw_line=line.strip(), title=title, company=company)


def extract_experience_entries(experience_text: str) -> list[ExperienceEntry]:
    """Parse every non-empty line of the experience section into an entry."""
    return [parse_experience_entry(line) for line in experience_text.splitlines() if line.strip()]
