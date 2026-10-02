from pathlib import Path

from .contact_fields import extract_contact_fields
from .extract_text import extract_text, is_text_sparse
from .layout import has_multi_column_layout
from .models import ContactInfo, ParsedResume, ResumeSection
from .sections import split_into_sections
from .skills_taxonomy import normalize_skills, split_raw_skills


def parse_resume(path: Path) -> ParsedResume:
    """Parse a CV file end-to-end: extract text, contacts, sections and skills."""
    text = extract_text(path)
    contact = ContactInfo(**extract_contact_fields(text))
    sections = split_into_sections(text)
    skills = normalize_skills(split_raw_skills(sections.get("skills", "")))
    return ParsedResume(
        contact=contact,
        sections=[
            ResumeSection(name=name, content=content)
            for name, content in sections.items()
        ],
        skills=skills,
        multi_column_layout=has_multi_column_layout(path),
        low_text_content=is_text_sparse(text),
    )


__all__ = ["parse_resume", "ParsedResume", "ContactInfo", "ResumeSection"]
