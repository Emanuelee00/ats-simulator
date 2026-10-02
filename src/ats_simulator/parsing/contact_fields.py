import re

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"(?:\+\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}")
_LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?", re.IGNORECASE)
_GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w-]+/?", re.IGNORECASE)


def extract_email(text: str) -> str | None:
    """Find the first email address in the text, if any."""
    match = _EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Find the first phone-number-like sequence in the text, if any."""
    match = _PHONE_RE.search(text)
    return match.group(0) if match else None


def extract_links(text: str) -> dict:
    """Find LinkedIn and GitHub profile URLs in the text, if any."""
    linkedin = _LINKEDIN_RE.search(text)
    github = _GITHUB_RE.search(text)
    return {
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
    }


def extract_contact_fields(text: str) -> dict:
    """Aggregate all contact fields found in the text."""
    links = extract_links(text)
    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": links["linkedin"],
        "github": links["github"],
    }
