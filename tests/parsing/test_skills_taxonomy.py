from ats_simulator.parsing.skills_taxonomy import (
    load_taxonomy,
    normalize_skills,
    split_raw_skills,
)


def test_taxonomy_csv_loads():
    taxonomy = load_taxonomy()
    assert len(taxonomy) > 50
    assert taxonomy["python"] == "Python"


def test_taxonomy_maps_synonyms_and_abbreviations_to_same_canonical():
    taxonomy = load_taxonomy()
    assert taxonomy["ml"] == "Machine Learning"
    assert taxonomy["machine learning"] == "Machine Learning"


def test_split_raw_skills_comma_separated():
    assert split_raw_skills("Python, SQL, Docker") == ["Python", "SQL", "Docker"]


def test_split_raw_skills_bullet_lines():
    text = "- Python\n* SQL\n• Docker"
    assert split_raw_skills(text) == ["Python", "SQL", "Docker"]


def test_normalize_skills_collapses_synonyms_and_dedupes():
    normalized = normalize_skills(["ML", "machine learning", "Python", "py"])
    assert normalized == ["Machine Learning", "Python"]


def test_normalize_skills_passes_through_unknown_skill():
    normalized = normalize_skills(["Some Niche Tool"])
    assert normalized == ["Some Niche Tool"]
