from datetime import date

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel

from .experience_dates import DateRange


class EmploymentGap(BaseModel):
    start: date
    end: date


def _merge_intervals(intervals: list[tuple[date, date]]) -> list[tuple[date, date]]:
    """Merge overlapping or touching (start, end) intervals, sorted by start."""
    merged: list[tuple[date, date]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def compute_total_experience_years(ranges: list[DateRange], today: date | None = None) -> float:
    """Sum non-overlapping experience duration in years."""
    today = today or date.today()
    intervals = [(r.start, r.end or today) for r in ranges]
    merged = _merge_intervals(intervals)
    total_days = sum((end - start).days for start, end in merged)
    return round(total_days / 365.25, 1)


def detect_employment_gaps(
    ranges: list[DateRange], gap_threshold_months: int = 6, today: date | None = None
) -> list[EmploymentGap]:
    """Find gaps of at least `gap_threshold_months` between experience periods."""
    today = today or date.today()
    intervals = [(r.start, r.end or today) for r in ranges]
    merged = _merge_intervals(intervals)

    gaps = []
    for (_, prev_end), (next_start, _) in zip(merged, merged[1:]):
        delta = relativedelta(next_start, prev_end)
        if delta.years * 12 + delta.months >= gap_threshold_months:
            gaps.append(EmploymentGap(start=prev_end, end=next_start))
    return gaps
