from ats_simulator.parsing.models import ContactInfo, ParsedResume, ResumeSection


def test_contact_info_all_fields():
    contact = ContactInfo(email="a@b.com", phone="123", linkedin="li", github="gh")
    assert contact.email == "a@b.com"
    assert contact.github == "gh"


def test_contact_info_missing_fields_default_none():
    contact = ContactInfo(email="a@b.com")
    assert contact.phone is None
    assert contact.linkedin is None


def test_resume_section_basic():
    section = ResumeSection(name="experience", content="Did stuff")
    assert section.name == "experience"
    assert section.content == "Did stuff"


def test_parsed_resume_aggregates():
    resume = ParsedResume(
        contact=ContactInfo(email="a@b.com"),
        sections=[ResumeSection(name="skills", content="Python")],
    )
    assert resume.contact.email == "a@b.com"
    assert resume.sections[0].name == "skills"
