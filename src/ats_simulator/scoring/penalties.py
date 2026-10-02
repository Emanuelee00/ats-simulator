_LAYOUT_PENALTY = 15
_TABLE_PENALTY = 20
_LOW_TEXT_SCORE_CAP = 5


def apply_layout_penalty(score: int, multi_column_layout: bool) -> int:
    """Penalize layouts that simpler ATS parsers are more likely to misread."""
    if multi_column_layout:
        return max(0, score - _LAYOUT_PENALTY)
    return score


def apply_table_penalty(score: int, has_tables: bool) -> int:
    """Penalize genuine PDF tables — a known harder case than column layouts.

    Cell reading order from a ruled table can get scrambled by simpler
    ATS parsers even more unpredictably than a plain multi-column layout.
    """
    if has_tables:
        return max(0, score - _TABLE_PENALTY)
    return score


def apply_low_text_penalty(score: int, low_text_content: bool) -> int:
    """Cap the score when extracted text is too sparse to be a real CV.

    This is the most severe real-world ATS failure mode: a scanned/image
    CV is unreadable by almost any ATS, regardless of any other signal.
    """
    if low_text_content:
        return min(score, _LOW_TEXT_SCORE_CAP)
    return score
