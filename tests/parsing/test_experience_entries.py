from ats_simulator.parsing.experience_entries import (
    extract_experience_entries,
    parse_experience_entry,
)


def test_parse_experience_entry_presso_separator():
    entry = parse_experience_entry("Senior Developer presso Acme Corp")
    assert entry.title == "Senior Developer"
    assert entry.company == "Acme Corp"


def test_parse_experience_entry_at_separator():
    entry = parse_experience_entry("Senior Developer at Acme Corp")
    assert entry.title == "Senior Developer"
    assert entry.company == "Acme Corp"


def test_parse_experience_entry_pipe_separator():
    entry = parse_experience_entry("Senior Developer | Acme Corp")
    assert entry.title == "Senior Developer"
    assert entry.company == "Acme Corp"


def test_parse_experience_entry_dash_separator():
    entry = parse_experience_entry("Senior Developer - Acme Corp")
    assert entry.title == "Senior Developer"
    assert entry.company == "Acme Corp"


def test_parse_experience_entry_no_separator_keeps_raw_as_title():
    entry = parse_experience_entry("Built scalable backend systems")
    assert entry.title == "Built scalable backend systems"
    assert entry.company is None


def test_extract_experience_entries_multiple_lines():
    text = "Senior Developer at Acme Corp\nBuilt scalable systems\nJunior Dev presso Beta Srl"
    entries = extract_experience_entries(text)
    assert len(entries) == 3
    assert entries[0].company == "Acme Corp"
    assert entries[2].company == "Beta Srl"
