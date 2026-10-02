import json
from datetime import date

from openai import OpenAI

from .ai_backend import ExtractedEntities
from .experience_dates import DateRange

_MODEL = "gpt-4o-mini"

_RESPONSE_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "resume_entities",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "candidate_name": {"type": ["string", "null"]},
                "organizations": {"type": "array", "items": {"type": "string"}},
                "date_ranges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string"},
                            "end": {"type": ["string", "null"]},
                        },
                        "required": ["start", "end"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["candidate_name", "organizations", "date_ranges"],
            "additionalProperties": False,
        },
    },
}

_SYSTEM_PROMPT = (
    "Extract structured data from CV/resume text. Identify the candidate's "
    "name (usually near the top), organizations/employers mentioned, and "
    "employment date ranges. Dates may appear in any language or format "
    "(e.g. 'Jan 2021 - Present', 'da marzo 2021 a oggi', 'in corso', "
    "'2019-2021'). Normalize each date to 'YYYY-MM', or 'YYYY' if no month "
    "is given. Use null for an end date meaning the position is still "
    "ongoing (e.g. 'Present', 'presente', 'oggi', 'in corso', 'current')."
)


def _parse_date_token(token: str) -> date:
    parts = token.split("-")
    if len(parts) == 2:
        return date(int(parts[0]), int(parts[1]), 1)
    return date(int(parts[0]), 1, 1)


class LLMEntityExtractor:
    """EntityExtractor backed by an OpenAI structured-output chat completion.

    Never raises: any network/API/schema failure returns an empty
    ExtractedEntities, falling back to the regex/heuristic extraction in
    experience_dates.py / candidate_name.py / experience_entries.py.
    """

    def __init__(self, client: OpenAI | None = None, model: str = _MODEL):
        self._client = client or OpenAI()
        self._model = model

    def extract(self, text: str) -> ExtractedEntities:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                response_format=_RESPONSE_SCHEMA,
            )
            data = json.loads(response.choices[0].message.content)
            date_ranges = [
                DateRange(
                    start=_parse_date_token(r["start"]),
                    end=_parse_date_token(r["end"]) if r["end"] else None,
                )
                for r in data.get("date_ranges", [])
            ]
            return ExtractedEntities(
                candidate_name=data.get("candidate_name"),
                organizations=data.get("organizations", []),
                date_ranges=date_ranges,
            )
        except Exception:
            return ExtractedEntities()


def create_default_extractor() -> "LLMEntityExtractor | None":
    """Build the default extractor, or None if no API key is configured."""
    try:
        return LLMEntityExtractor()
    except Exception:
        return None
