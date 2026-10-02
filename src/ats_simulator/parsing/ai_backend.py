from typing import Protocol

from pydantic import BaseModel

from .experience_dates import DateRange


class SectionClassifier(Protocol):
    """Classifies a heading-shaped CV line into a canonical section name.

    Any implementation (embedding similarity, an LLM call, a future API)
    can be swapped in without changing parse_resume() or the rest of the
    pipeline, as long as it honors this contract.
    """

    def classify(self, line: str) -> str | None: ...


class ExtractedEntities(BaseModel):
    candidate_name: str | None = None
    organizations: list[str] = []
    date_ranges: list[DateRange] = []


class EntityExtractor(Protocol):
    """Extracts candidate name, organizations and employment date ranges.

    Same pluggability contract as SectionClassifier: swap the backend
    (local model, LLM API) without touching callers.
    """

    def extract(self, text: str) -> ExtractedEntities: ...
