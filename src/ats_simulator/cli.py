import argparse
from pathlib import Path

from .parsing import ParsedResume
from .parsing import parse_resume as _parse_resume
from .scoring import ATSScoreResult
from .scoring import score_resume as _score_resume


def _format_report(parsed: ParsedResume, result: ATSScoreResult) -> str:
    lines = [
        f"Email: {parsed.contact.email or '-'}",
        f"Telefono: {parsed.contact.phone or '-'}",
        f"LinkedIn: {parsed.contact.linkedin or '-'}",
        f"GitHub: {parsed.contact.github or '-'}",
        f"Sezioni trovate: {', '.join(s.name for s in parsed.sections) or '-'}",
        f"Skills normalizzate: {', '.join(parsed.skills) or '-'}",
        "",
        f"ATS Score: {result.score}/100",
        f"  Contatti: +{result.breakdown.contact_points}  Sezioni: +{result.breakdown.sections_points}"
        f"  Layout: {result.breakdown.layout_penalty}  Tabelle: {result.breakdown.table_penalty}"
        + ("  [punteggio limitato: testo scarso]" if result.breakdown.low_text_cap_applied else ""),
    ]
    if result.issues:
        lines.append("Problemi rilevati:")
        lines += [f"  - {issue}" for issue in result.issues]
    else:
        lines.append("Nessun problema rilevato.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(prog="ats-simulator")
    parser.add_argument("command", choices=["score"])
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    parsed = _parse_resume(args.path)
    result = _score_resume(parsed)
    print(_format_report(parsed, result))


if __name__ == "__main__":
    main()
