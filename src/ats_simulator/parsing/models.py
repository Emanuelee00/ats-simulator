from pydantic import BaseModel


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
