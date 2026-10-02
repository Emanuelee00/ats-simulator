import re

from ats_simulator.parsing.contact_fields import (
    extract_contact_fields,
    extract_email,
    extract_links,
    extract_phone,
)


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def test_extract_email_variants():
    assert extract_email("Contact: mario.rossi@email.com") == "mario.rossi@email.com"
    assert extract_email("reach me at m.rossi+jobs@sub.domain.co.uk") == "m.rossi+jobs@sub.domain.co.uk"
    assert extract_email("no email here") is None


def test_extract_phone_variants():
    # Scope: supports "+<country>" prefix or plain national format.
    # The alternative "00<country>" international prefix is out of scope
    # (rare on CVs, and ambiguous with a plain area-code match).
    assert _digits(extract_phone("Tel: +39 333 1234567")) == "393331234567"
    assert _digits(extract_phone("Mobile: +1 555 1234567")) == "15551234567"
    assert _digits(extract_phone("Call 333-123-4567")) == "3331234567"
    assert _digits(extract_phone("(555) 123-4567")) == "5551234567"


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
    assert _digits(fields["phone"]) == "393331234567"
    assert fields["linkedin"] == "linkedin.com/in/mario-rossi"
    assert fields["github"] == "github.com/mariorossi"
