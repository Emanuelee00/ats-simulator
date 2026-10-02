from pathlib import Path

import pdfplumber
from pydantic import BaseModel


class Word(BaseModel):
    text: str
    x0: float
    x1: float
    top: float


def extract_words_with_position(path: Path) -> list[Word]:
    """Extract every word from a PDF with its bounding-box coordinates."""
    words = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for w in page.extract_words():
                words.append(Word(text=w["text"], x0=w["x0"], x1=w["x1"], top=w["top"]))
    return words


def _group_lines(words: list[Word], tolerance: float = 2.0) -> list[list[Word]]:
    """Group words into lines by closeness of their vertical position."""
    lines: list[list[Word]] = []
    for word in sorted(words, key=lambda w: (w.top, w.x0)):
        for line in lines:
            if abs(line[0].top - word.top) <= tolerance:
                line.append(word)
                break
        else:
            lines.append([word])
    return lines


def detect_column_gaps(
    words: list[Word], min_gap: float = 40.0, min_recurrence: float = 0.4
) -> list[float]:
    """Detect horizontal gaps wide and frequent enough to be column separators."""
    multi_word_lines = [line for line in _group_lines(words) if len(line) > 1]
    if not multi_word_lines:
        return []

    gap_positions = []
    for line in multi_word_lines:
        ordered = sorted(line, key=lambda w: w.x0)
        for a, b in zip(ordered, ordered[1:]):
            gap = b.x0 - a.x1
            if gap >= min_gap:
                gap_positions.append((a.x1 + b.x0) / 2)

    clusters: list[list[float]] = []
    for pos in sorted(gap_positions):
        if clusters and pos - clusters[-1][-1] <= 20.0:
            clusters[-1].append(pos)
        else:
            clusters.append([pos])

    threshold = max(1, int(len(multi_word_lines) * min_recurrence))
    return [sum(c) / len(c) for c in clusters if len(c) >= threshold]


def reorder_columns(words: list[Word], gaps: list[float]) -> str:
    """Reorder words into column-by-column reading order using detected gaps."""
    boundaries = sorted(gaps)
    columns: list[list[Word]] = [[] for _ in range(len(boundaries) + 1)]
    for word in words:
        index = sum(1 for b in boundaries if word.x0 >= b)
        columns[index].append(word)

    column_texts = []
    for column_words in columns:
        lines = sorted(_group_lines(column_words), key=lambda line: line[0].top)
        line_texts = [
            " ".join(w.text for w in sorted(line, key=lambda w: w.x0)) for line in lines
        ]
        column_texts.append("\n".join(line_texts))
    return "\n".join(t for t in column_texts if t)
