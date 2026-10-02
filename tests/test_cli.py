import sys

from ats_simulator.cli import _format_report, main
from ats_simulator.parsing.models import ContactInfo, ParsedResume
from ats_simulator.scoring.models import ATSScoreResult
from tests.fixtures import make_pdf


def test_format_report_includes_contact_score_and_issues():
    parsed = ParsedResume(contact=ContactInfo(email="a@b.com"), sections=[])
    result = ATSScoreResult(score=42, issues=["Problema X"])

    report = _format_report(parsed, result)

    assert "a@b.com" in report
    assert "42/100" in report
    assert "Problema X" in report


def test_format_report_no_issues_message():
    parsed = ParsedResume(contact=ContactInfo(), sections=[])
    result = ATSScoreResult(score=100, issues=[])

    report = _format_report(parsed, result)

    assert "Nessun problema rilevato." in report


def test_main_end_to_end_on_real_cv(tmp_path, capsys, monkeypatch):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(
        pdf_path,
        [
            "Mario Rossi",
            "mario.rossi@email.com",
            "Experience",
            "Senior Developer",
            "Skills",
            "Python, SQL",
        ],
    )
    monkeypatch.setattr(sys, "argv", ["ats-simulator", "score", str(pdf_path)])

    main()

    out = capsys.readouterr().out
    assert "mario.rossi@email.com" in out
    assert "ATS Score" in out
    assert "Python" in out
