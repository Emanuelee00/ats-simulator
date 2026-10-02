from pathlib import Path

from .candidate_name import extract_candidate_name
from .contact_fields import extract_contact_fields
from .education_taxonomy import normalize_education_level
from .embedding_classifier import create_default_classifier
from .experience_analysis import compute_total_experience_years, detect_employment_gaps
from .experience_dates import find_date_range_candidates, parse_date_range
from .experience_entries import extract_experience_entries
from .extract_text import extract_text, is_text_sparse
from .layout import has_multi_column_layout
from .llm_extractor import create_default_extractor
from .models import ContactInfo, ParsedResume, ResumeSection
from .sections import split_into_sections
from .skills_taxonomy import normalize_skills, split_raw_skills
from .tables import has_pdf_tables

# Built once per process, not per parse_resume() call: both return None
# without an API key, so the library stays fully usable with zero AI setup.
_classifier = create_default_classifier()
_extractor = create_default_extractor()


def _extract_experience_dates(experience_text: str) -> list:
    candidates = find_date_range_candidates(experience_text)
    parsed = [parse_date_range(c) for c in candidates]
    return [r for r in parsed if r is not None]


def parse_resume(path: Path) -> ParsedResume:
    """Parse a CV file end-to-end: extract text, contacts, sections and skills.

    Section headings and employment dates/candidate name get an AI-assisted
    second pass (OpenAI embeddings/LLM, see ai_backend.py) when an API key
    is configured; otherwise this runs entirely on the regex/heuristic
    tier, unchanged from before Fase 19-23.
    """
    text = extract_text(path)
    contact = ContactInfo(**extract_contact_fields(text))
    sections = split_into_sections(text, classifier=_classifier)
    skills = normalize_skills(split_raw_skills(sections.get("skills", "")))

    llm_entities = _extractor.extract(text) if _extractor else None
    date_ranges = (llm_entities.date_ranges if llm_entities else []) or _extract_experience_dates(
        sections.get("experience", "")
    )
    total_years = compute_total_experience_years(date_ranges) if date_ranges else None
    gaps = detect_employment_gaps(date_ranges) if date_ranges else []
    candidate_name = (llm_entities.candidate_name if llm_entities else None) or extract_candidate_name(text)

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
        candidate_name=candidate_name,
        experience_entries=extract_experience_entries(sections.get("experience", "")),
        education_level=normalize_education_level(sections.get("education", "")),
        has_tables=has_pdf_tables(path),
    )


__all__ = ["parse_resume", "ParsedResume", "ContactInfo", "ResumeSection"]
