from ats_simulator.parsing.candidate_name import extract_candidate_name


def test_extract_candidate_name_first_line():
    text = "Mario Rossi\nmario.rossi@email.com\nExperience\n..."
    assert extract_candidate_name(text) == "Mario Rossi"


def test_extract_candidate_name_skips_email_first_line():
    text = "mario.rossi@email.com\nMario Rossi\nExperience\n..."
    assert extract_candidate_name(text) == "Mario Rossi"


def test_extract_candidate_name_skips_phone_like_line():
    text = "+39 333 1234567\nMario Rossi\n..."
    assert extract_candidate_name(text) == "Mario Rossi"


def test_extract_candidate_name_empty_text_returns_none():
    assert extract_candidate_name("") is None
