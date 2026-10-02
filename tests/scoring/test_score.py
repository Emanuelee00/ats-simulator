from ats_simulator.parsing.models import ContactInfo, ParsedResume, ResumeSection
from ats_simulator.scoring.score import build_issues, score_from_parsed, score_resume


def _full_resume(
    multi_column: bool = False, low_text: bool = False, has_tables: bool = False
) -> ParsedResume:
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
        low_text_content=low_text,
        has_tables=has_tables,
    )


def _empty_resume() -> ParsedResume:
    return ParsedResume(contact=ContactInfo(), sections=[])


def test_score_from_parsed_full_resume_scores_100():
    assert score_from_parsed(_full_resume()) == 100


def test_score_from_parsed_empty_resume_scores_0():
    assert score_from_parsed(_empty_resume()) == 0


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


def test_score_resume_low_text_content_overrides_everything():
    # Even a resume that looks otherwise "complete" gets capped: if the
    # text is this sparse, real ATS engines won't read it either.
    scanned = score_resume(_full_resume(low_text=True))
    assert scanned.score <= 5
    assert any("scansione" in issue.lower() for issue in scanned.issues)


def test_score_resume_table_detected():
    result = score_resume(_full_resume(has_tables=True))
    assert result.score == 80
    assert any("tabella" in issue.lower() for issue in result.issues)


def test_score_resume_breakdown_sums_to_score_without_low_text_cap():
    result = score_resume(_full_resume(multi_column=True, has_tables=True))
    b = result.breakdown
    assert b.contact_points + b.sections_points + b.layout_penalty + b.table_penalty == result.score


def test_score_resume_breakdown_reflects_clamped_penalty():
    # An empty resume (score 0) hitting a multi-column penalty: the penalty
    # can't push the score below 0, so the breakdown must show the real
    # applied delta (0), not the flat constant (-15) that didn't fully apply.
    empty_multicolumn = ParsedResume(
        contact=ContactInfo(), sections=[], multi_column_layout=True
    )
    result = score_resume(empty_multicolumn)
    assert result.score == 0
    assert result.breakdown.layout_penalty == 0


def test_score_resume_breakdown_flags_low_text_cap():
    result = score_resume(_full_resume(low_text=True))
    assert result.breakdown.low_text_cap_applied is True
