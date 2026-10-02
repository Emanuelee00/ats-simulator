from ats_simulator.parsing.education_taxonomy import (
    load_education_taxonomy,
    normalize_education_level,
)


def test_taxonomy_loads():
    taxonomy = load_education_taxonomy()
    assert len(taxonomy) > 10


def test_normalize_bachelor_from_free_text():
    text = "Laurea Triennale in Informatica, Università di Milano, 2020"
    assert normalize_education_level(text) == "Bachelor's Degree"


def test_normalize_master_not_shadowed_by_bachelor_substring():
    # "laurea magistrale" contains "laurea", which alone means Bachelor's —
    # the longer, more specific phrase must win.
    text = "Laurea Magistrale in Ingegneria Informatica"
    assert normalize_education_level(text) == "Master's Degree"


def test_normalize_phd():
    assert normalize_education_level("Dottorato di Ricerca in Fisica") == "PhD"


def test_normalize_no_match_returns_none():
    assert normalize_education_level("Corso di formazione interno") is None
