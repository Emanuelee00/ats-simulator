from pathlib import Path

from .candidate_name import extract_candidate_name
from .contact_fields import extract_contact_fields
from .experience_analysis import compute_total_experience_years, detect_employment_gaps
from .experience_dates import find_date_range_candidates, parse_date_range
from .experience_entries import extract_experience_entries
from .extract_text import extract_text, is_text_sparse
from .layout import has_multi_column_layout
from .models import ContactInfo, ParsedResume, ResumeSection
from .sections import split_into_sections
from .skills_taxonomy import normalize_skills, split_raw_skills


def _extract_experience_dates(experience_text: str) -> list:
    candidates = find_date_range_candidates(experience_text)
    parsed = [parse_date_range(c) for c in candidates]
    return [r for r in parsed if r is not None]


def parse_resume(path: Path) -> ParsedResume:
    """Parse a CV file end-to-end: extract text, contacts, sections and skills."""
    text = extract_text(path)
    contact = ContactInfo(**extract_contact_fields(text))
    sections = split_into_sections(text)
    skills = normalize_skills(split_raw_skills(sections.get("skills", "")))

    date_ranges = _extract_experience_dates(sections.get("experience", ""))
    total_years = compute_total_experience_years(date_ranges) if date_ranges else None
    gaps = detect_employment_gaps(date_ranges) if date_ranges else []

    return ParsedResume(
        contact=contact,
        sections=[
            ResumeSection(name=name, content=content)
            for name, content in sections.items()
        ],
        skills=skills,
        multi_column_layout=has_multi_column_layout(path),
        low_text_content=is_text_sparse(text),
        total_experience_years=total_years,
        employment_gaps=gaps,
        candidate_name=extract_candidate_name(text),
        experience_entries=extract_experience_entries(sections.get("experience", "")),
    )


__all__ = ["parse_resume", "ParsedResume", "ContactInfo", "ResumeSection"]
