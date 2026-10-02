from ats_simulator.parsing.models import ContactInfo, ParsedResume, ResumeSection
from ats_simulator.scoring.score import (
    apply_layout_penalty,
    build_issues,
    score_from_parsed,
    score_resume,
)


def _full_resume(multi_column: bool = False) -> ParsedResume:
    return ParsedResume(
        contact=ContactInfo(
            email="a@b.com", phone="123", linkedin="li.com/in/a", github="gh.com/a"
        ),
        sections=[
            ResumeSection(name="experience", content="Did stuff"),
            ResumeSection(name="education", content="Studied stuff"),
            ResumeSection(name="skills", content="Python"),
        ],
        skills=["Python"],
        multi_column_layout=multi_column,
    )


def _empty_resume() -> ParsedResume:
    return ParsedResume(contact=ContactInfo(), sections=[])


def test_score_from_parsed_full_resume_scores_100():
    assert score_from_parsed(_full_resume()) == 100


def test_score_from_parsed_empty_resume_scores_0():
    assert score_from_parsed(_empty_resume()) == 0


def test_apply_layout_penalty_reduces_score_when_multicolumn():
    assert apply_layout_penalty(100, multi_column_layout=True) == 85
    assert apply_layout_penalty(100, multi_column_layout=False) == 100


def test_apply_layout_penalty_floors_at_zero():
    assert apply_layout_penalty(10, multi_column_layout=True) == 0


def test_build_issues_flags_missing_fields():
    issues = build_issues(_empty_resume())
    assert any("email" in issue.lower() for issue in issues)
    assert any("esperienza" in issue.lower() for issue in issues)


def test_build_issues_empty_for_full_clean_resume():
    assert build_issues(_full_resume(multi_column=False)) == []


def test_score_resume_clean_vs_problematic_resume():
    clean = score_resume(_full_resume(multi_column=False))
    problematic = score_resume(_full_resume(multi_column=True))

    assert clean.score == 100
    assert clean.issues == []
    assert problematic.score == 85
    assert any("colonna" in issue.lower() for issue in problematic.issues)
