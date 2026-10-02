import re

import phonenumbers

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_LINKEDIN_RE = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?", re.IGNORECASE)
_GITHUB_RE = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w-]+/?", re.IGNORECASE)

_DEFAULT_REGION = "IT"


def extract_email(text: str) -> str | None:
    """Find the first email address in the text, if any."""
    match = _EMAIL_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str, region_hint: str = _DEFAULT_REGION) -> str | None:
    """Find the first valid phone number in the text, normalized to E.164.

    Uses Google's libphonenumber (via `phonenumbers`) instead of a hand-written
    regex: it correctly validates and normalizes real-world international
    formats (e.g. the "00<country>" prefix, which previously truncated
    matches — see git history) that a regex kept getting subtly wrong.
    `region_hint` is only used to interpret numbers with no explicit country
    code; numbers with "+<country>" are parsed correctly regardless.
    """
    matches = phonenumbers.PhoneNumberMatcher(text, region_hint)
    for match in matches:
        return phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
    return None


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
