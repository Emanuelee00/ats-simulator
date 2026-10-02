from ats_simulator.parsing.contact_fields import (
    extract_contact_fields,
    extract_email,
    extract_links,
    extract_phone,
)


def test_extract_email_variants():
    assert extract_email("Contact: mario.rossi@email.com") == "mario.rossi@email.com"
    assert extract_email("reach me at m.rossi+jobs@sub.domain.co.uk") == "m.rossi+jobs@sub.domain.co.uk"
    assert extract_email("no email here") is None


def test_extract_phone_variants_normalized_to_e164():
    assert extract_phone("Tel: +39 333 1234567") == "+393331234567"
    assert extract_phone("Call 333-123-4567") == "+393331234567"
    assert extract_phone("+1 212 9876543") == "+12129876543"
    assert extract_phone("+44 20 7946 0958") == "+442079460958"


def test_extract_phone_00_prefix_now_works():
    # Previously a known, documented bug: the "00<country>" international
    # prefix made a hand-written regex pick a wrong, truncated match.
    # phonenumbers (libphonenumber) handles it correctly.
    assert extract_phone("Phone: 0039 333 1234567") == "+393331234567"


def test_extract_phone_no_match_returns_none():
    assert extract_phone("no phone number in this text") is None


def test_extract_links():
    text = "Profile: https://www.linkedin.com/in/mario-rossi and github.com/mariorossi"
    links = extract_links(text)
    assert links["linkedin"] == "https://www.linkedin.com/in/mario-rossi"
    assert links["github"] == "github.com/mariorossi"


def test_extract_links_missing():
    links = extract_links("no social links here")
    assert links == {"linkedin": None, "github": None}


def test_extract_contact_fields_integration():
    text = (
        "Mario Rossi\n"
        "mario.rossi@email.com | +39 333 1234567\n"
        "linkedin.com/in/mario-rossi | github.com/mariorossi\n"
    )
    fields = extract_contact_fields(text)
    assert fields["email"] == "mario.rossi@email.com"
    assert fields["phone"] == "+393331234567"
    assert fields["linkedin"] == "linkedin.com/in/mario-rossi"
    assert fields["github"] == "github.com/mariorossi"
