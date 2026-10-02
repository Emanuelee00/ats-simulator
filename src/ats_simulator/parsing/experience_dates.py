import re
from datetime import date, datetime

from dateutil import parser as date_parser
from pydantic import BaseModel

_IT_MONTHS = {
    "gen": "jan",
    "gennaio": "january",
    "feb": "feb",
    "febbraio": "february",
    "mar": "mar",
    "marzo": "march",
    "apr": "apr",
    "aprile": "april",
    "mag": "may",
    "maggio": "may",
    "giu": "jun",
    "giugno": "june",
    "lug": "jul",
    "luglio": "july",
    "ago": "aug",
    "agosto": "august",
    "set": "sep",
    "settembre": "september",
    "ott": "oct",
    "ottobre": "october",
    "nov": "nov",
    "novembre": "november",
    "dic": "dec",
    "dicembre": "december",
}
_MONTH_PATTERN = r"(?:" + "|".join(_IT_MONTHS) + "|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?" + r")\.?"
_DATE_TOKEN = rf"(?:{_MONTH_PATTERN}[ \t]+\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})"
_CURRENT_WORDS = {"presente", "oggi", "current", "now", "in corso"}
_RANGE_RE = re.compile(
    rf"({_DATE_TOKEN})\s*[-–—]\s*({_DATE_TOKEN}|{'|'.join(_CURRENT_WORDS)})",
    re.IGNORECASE,
)


class DateRange(BaseModel):
    start: date
    end: date | None = None


def _translate_italian_month(raw: str) -> str:
    """Translate a leading Italian month name/abbreviation to English.

    dateutil's parser only recognizes English month names/abbreviations —
    without this, "Gen 2020" or "Dic 2022" fail to parse entirely.
    """
    parts = raw.strip().split(maxsplit=1)
    if len(parts) == 2 and parts[0].lower().rstrip(".") in _IT_MONTHS:
        return f"{_IT_MONTHS[parts[0].lower().rstrip('.')]} {parts[1]}"
    return raw


def find_date_range_candidates(text: str) -> list[str]:
    """Isolate raw date-range spans like 'Gen 2020 - Dic 2022' or '2019-2021'."""
    return [m.group(0) for m in _RANGE_RE.finditer(text)]


def parse_date_range(raw: str) -> DateRange | None:
    """Parse a raw date-range span into a DateRange, or None if unparseable."""
    match = _RANGE_RE.search(raw)
    if not match:
        return None

    default = datetime(1900, 1, 1)
    try:
        start = date_parser.parse(_translate_italian_month(match.group(1)), default=default).date()
    except (ValueError, OverflowError):
        return None

    end_raw = match.group(2).strip()
    if end_raw.lower() in _CURRENT_WORDS:
        return DateRange(start=start, end=None)
    try:
        end = date_parser.parse(_translate_italian_month(end_raw), default=default).date()
    except (ValueError, OverflowError):
        return None
    return DateRange(start=start, end=end)
