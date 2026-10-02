from pydantic import BaseModel

from .experience_analysis import EmploymentGap
from .experience_entries import ExperienceEntry


class ContactInfo(BaseModel):
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None


class ResumeSection(BaseModel):
    name: str
    content: str


class ParsedResume(BaseModel):
    contact: ContactInfo
    sections: list[ResumeSection]
    skills: list[str] = []
    multi_column_layout: bool = False
    low_text_content: bool = False
    total_experience_years: float | None = None
    employment_gaps: list[EmploymentGap] = []
    candidate_name: str | None = None
    experience_entries: list[ExperienceEntry] = []
    education_level: str | None = None
