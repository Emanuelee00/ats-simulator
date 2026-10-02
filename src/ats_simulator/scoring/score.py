from ats_simulator.parsing.models import ParsedResume

from .models import ATSScoreResult

_LAYOUT_PENALTY = 15
_LOW_TEXT_SCORE_CAP = 5


def score_from_parsed(parsed: ParsedResume) -> int:
    """Base score (0-100) from contact completeness and standard sections found."""
    score = 0
    if parsed.contact.email:
        score += 15
    if parsed.contact.phone:
        score += 10
    if parsed.contact.linkedin or parsed.contact.github:
        score += 10

    section_names = {s.name for s in parsed.sections}
    if "experience" in section_names:
        score += 25
    if "education" in section_names:
        score += 20
    if "skills" in section_names:
        score += 20
    return score


def apply_layout_penalty(score: int, multi_column_layout: bool) -> int:
    """Penalize layouts that simpler ATS parsers are more likely to misread."""
    if multi_column_layout:
        return max(0, score - _LAYOUT_PENALTY)
    return score


def apply_low_text_penalty(score: int, low_text_content: bool) -> int:
    """Cap the score when extracted text is too sparse to be a real CV.

    This is the most severe real-world ATS failure mode: a scanned/image
    CV is unreadable by almost any ATS, regardless of any other signal.
    """
    if low_text_content:
        return min(score, _LOW_TEXT_SCORE_CAP)
    return score


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
    return issues


def score_resume(parsed: ParsedResume) -> ATSScoreResult:
    """Compute the final ATS-readability score and issue list for a resume."""
    base = score_from_parsed(parsed)
    with_layout = apply_layout_penalty(base, parsed.multi_column_layout)
    final = apply_low_text_penalty(with_layout, parsed.low_text_content)
    return ATSScoreResult(score=final, issues=build_issues(parsed))
