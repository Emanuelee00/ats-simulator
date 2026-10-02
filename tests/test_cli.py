import sys

from ats_simulator.cli import _format_report, main
from ats_simulator.parsing.models import ContactInfo, ParsedResume
from ats_simulator.scoring.models import ATSScoreResult, ScoreBreakdown
from tests.fixtures import make_pdf


def _result(score: int, issues: list[str], **breakdown_kwargs) -> ATSScoreResult:
    defaults = {"contact_points": 0, "sections_points": 0}
    breakdown = ScoreBreakdown(**{**defaults, **breakdown_kwargs})
    return ATSScoreResult(score=score, issues=issues, breakdown=breakdown)


def test_format_report_includes_contact_score_and_issues():
    parsed = ParsedResume(contact=ContactInfo(email="a@b.com"), sections=[])
    result = _result(42, ["Problema X"])

    report = _format_report(parsed, result)

    assert "a@b.com" in report
    assert "42/100" in report
    assert "Problema X" in report


def test_format_report_no_issues_message():
    parsed = ParsedResume(contact=ContactInfo(), sections=[])
    result = _result(100, [])

    report = _format_report(parsed, result)

    assert "Nessun problema rilevato." in report


def test_format_report_shows_breakdown():
    parsed = ParsedResume(contact=ContactInfo(email="a@b.com"), sections=[])
    result = _result(85, [], contact_points=15, sections_points=0, layout_penalty=-15)

    report = _format_report(parsed, result)

    assert "Layout: -15" in report


def test_format_report_flags_low_text_cap():
    parsed = ParsedResume(contact=ContactInfo(), sections=[])
    result = _result(5, [], low_text_cap_applied=True)

    report = _format_report(parsed, result)

    assert "punteggio limitato" in report


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
