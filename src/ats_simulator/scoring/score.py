from ats_simulator.parsing.models import ParsedResume

from .models import ATSScoreResult, ScoreBreakdown
from .penalties import apply_layout_penalty, apply_low_text_penalty, apply_table_penalty


def _contact_points(parsed: ParsedResume) -> int:
    points = 0
    if parsed.contact.email:
        points += 15
    if parsed.contact.phone:
        points += 10
    if parsed.contact.linkedin or parsed.contact.github:
        points += 10
    return points


def _sections_points(parsed: ParsedResume) -> int:
    section_names = {s.name for s in parsed.sections}
    points = 0
    if "experience" in section_names:
        points += 25
    if "education" in section_names:
        points += 20
    if "skills" in section_names:
        points += 20
    return points


def score_from_parsed(parsed: ParsedResume) -> int:
    """Base score (0-100) from contact completeness and standard sections found."""
    return _contact_points(parsed) + _sections_points(parsed)


def build_issues(parsed: ParsedResume) -> list[str]:
    """Human-readable list of problems found, for user-facing feedback."""
    issues = []
    if parsed.low_text_content:
        issues.append(
            "Il CV sembra basato su immagine o scansione: il testo estraibile "
            "è molto scarso. La maggior parte degli ATS reali non riesce a "
            "leggerlo senza OCR ed è di fatto invisibile al sistema."
        )
    if not parsed.contact.email:
        issues.append("Nessuna email trovata nel CV.")
    if not parsed.contact.phone:
        issues.append("Nessun numero di telefono trovato nel CV.")

    section_names = {s.name for s in parsed.sections}
    if "experience" not in section_names:
        issues.append("Sezione Esperienza non trovata o non riconosciuta.")
    if "education" not in section_names:
        issues.append("Sezione Formazione non trovata o non riconosciuta.")
    if "skills" not in section_names:
        issues.append("Sezione Competenze non trovata o non riconosciuta.")

    if parsed.multi_column_layout:
        issues.append(
            "Layout multi-colonna rilevato: alcuni ATS potrebbero leggere "
            "le sezioni in ordine sbagliato."
        )
    if parsed.has_tables:
        issues.append(
            "Tabella rilevata nel PDF: molti ATS non riescono a leggere "
            "correttamente il contenuto delle tabelle."
        )

    for gap in parsed.employment_gaps:
        issues.append(
            f"Rilevato un periodo senza esperienza lavorativa tra {gap.start} "
            f"e {gap.end}."
        )
    return issues


def score_resume(parsed: ParsedResume) -> ATSScoreResult:
    """Compute the final ATS-readability score, transparent breakdown and issues.

    The breakdown records the actual delta each penalty applied (not a flat
    constant) so it stays honest when a penalty gets clamped at the score
    floor — e.g. a "-15" layout penalty that only reduced the score by 4
    points because it was already near zero shows up as -4, not -15.
    """
    contact_points = _contact_points(parsed)
    sections_points = _sections_points(parsed)
    score = contact_points + sections_points

    before = score
    score = apply_layout_penalty(score, parsed.multi_column_layout)
    layout_penalty = score - before

    before = score
    score = apply_table_penalty(score, parsed.has_tables)
    table_penalty = score - before

    score = apply_low_text_penalty(score, parsed.low_text_content)

    breakdown = ScoreBreakdown(
        contact_points=contact_points,
        sections_points=sections_points,
        layout_penalty=layout_penalty,
        table_penalty=table_penalty,
        low_text_cap_applied=parsed.low_text_content,
    )
    return ATSScoreResult(score=score, issues=build_issues(parsed), breakdown=breakdown)
