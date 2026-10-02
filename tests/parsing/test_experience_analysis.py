from datetime import date

from ats_simulator.parsing.experience_analysis import (
    compute_total_experience_years,
    detect_employment_gaps,
)
from ats_simulator.parsing.experience_dates import DateRange


def test_compute_total_experience_years_non_overlapping():
    ranges = [
        DateRange(start=date(2020, 1, 1), end=date(2021, 1, 1)),
        DateRange(start=date(2022, 1, 1), end=date(2023, 1, 1)),
    ]
    assert compute_total_experience_years(ranges) == 2.0


def test_compute_total_experience_years_overlapping_not_double_counted():
    ranges = [
        DateRange(start=date(2020, 1, 1), end=date(2021, 6, 1)),
        DateRange(start=date(2021, 1, 1), end=date(2022, 1, 1)),
    ]
    # Overlap from 2021-01 to 2021-06-01 must not be counted twice.
    assert compute_total_experience_years(ranges) == 2.0


def test_compute_total_experience_years_ongoing_uses_today():
    ranges = [DateRange(start=date(2020, 1, 1), end=None)]
    years = compute_total_experience_years(ranges, today=date(2023, 1, 1))
    assert years == 3.0


def test_detect_employment_gaps_flags_long_gap():
    ranges = [
        DateRange(start=date(2020, 1, 1), end=date(2020, 6, 1)),
        DateRange(start=date(2021, 6, 1), end=date(2022, 1, 1)),
    ]
    gaps = detect_employment_gaps(ranges)
    assert len(gaps) == 1
    assert gaps[0].start == date(2020, 6, 1)
    assert gaps[0].end == date(2021, 6, 1)


def test_detect_employment_gaps_ignores_short_gap():
    ranges = [
        DateRange(start=date(2020, 1, 1), end=date(2020, 6, 1)),
        DateRange(start=date(2020, 8, 1), end=date(2021, 1, 1)),
    ]
    assert detect_employment_gaps(ranges) == []
