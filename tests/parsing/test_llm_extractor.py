import json
from datetime import date

from ats_simulator.parsing.llm_extractor import LLMEntityExtractor, _parse_date_token


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeResponse:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


class _FakeCompletions:
    def __init__(self, response_json):
        self._response_json = response_json

    def create(self, **kwargs):
        return _FakeResponse(json.dumps(self._response_json))


class _FakeChat:
    def __init__(self, response_json):
        self.completions = _FakeCompletions(response_json)


class _FakeClient:
    def __init__(self, response_json):
        self.chat = _FakeChat(response_json)


class _FailingCompletions:
    def create(self, **kwargs):
        raise RuntimeError("simulated network error")


class _FailingClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": _FailingCompletions()})()


def test_parse_date_token_year_month():
    assert _parse_date_token("2021-03") == date(2021, 3, 1)


def test_parse_date_token_year_only():
    assert _parse_date_token("2021") == date(2021, 1, 1)


def test_extract_parses_structured_response():
    # The model's job is understanding "Present"/"da...a..." in any language
    # (untestable offline); our job is correctly converting its structured
    # JSON output into ExtractedEntities, which this test covers.
    response_json = {
        "candidate_name": "Mario Rossi",
        "organizations": ["Acme Corp", "Beta Srl"],
        "date_ranges": [
            {"start": "2021-01", "end": None},
            {"start": "2018", "end": "2020"},
        ],
    }
    extractor = LLMEntityExtractor(client=_FakeClient(response_json))

    result = extractor.extract("some resume text")

    assert result.candidate_name == "Mario Rossi"
    assert result.organizations == ["Acme Corp", "Beta Srl"]
    assert result.date_ranges[0].start == date(2021, 1, 1)
    assert result.date_ranges[0].end is None
    assert result.date_ranges[1].start == date(2018, 1, 1)
    assert result.date_ranges[1].end == date(2020, 1, 1)


def test_extract_returns_empty_on_api_failure():
    extractor = LLMEntityExtractor(client=_FailingClient())

    result = extractor.extract("some resume text")

    assert result.candidate_name is None
    assert result.organizations == []
    assert result.date_ranges == []


def test_extract_returns_empty_on_malformed_json():
    class _MalformedCompletions:
        def create(self, **kwargs):
            return _FakeResponse("not valid json")

    client = type("Client", (), {})()
    client.chat = type("Chat", (), {"completions": _MalformedCompletions()})()

    result = LLMEntityExtractor(client=client).extract("text")

    assert result.candidate_name is None
