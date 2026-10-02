from datetime import date

from ats_simulator.parsing.experience_dates import (
    find_date_range_candidates,
    parse_date_range,
)


def test_find_date_range_candidates_common_formats():
    text = (
        "Esperienza\n"
        "Gen 2020 - Dic 2022: Senior Developer\n"
        "01/2020 - Presente: Consultant\n"
        "2019-2021: Analyst\n"
    )
    candidates = find_date_range_candidates(text)
    assert "Gen 2020 - Dic 2022" in candidates
    assert "01/2020 - Presente" in candidates
    assert "2019-2021" in candidates


def test_parse_date_range_italian_months():
    result = parse_date_range("Gen 2020 - Dic 2022")
    assert result.start == date(2020, 1, 1)
    assert result.end == date(2022, 12, 1)


def test_parse_date_range_english_months():
    result = parse_date_range("January 2020 - December 2022")
    assert result.start == date(2020, 1, 1)
    assert result.end == date(2022, 12, 1)


def test_parse_date_range_numeric_month_year():
    result = parse_date_range("01/2020 - 06/2022")
    assert result.start == date(2020, 1, 1)
    assert result.end == date(2022, 6, 1)


def test_parse_date_range_year_only():
    result = parse_date_range("2019-2021")
    assert result.start == date(2019, 1, 1)
    assert result.end == date(2021, 1, 1)


def test_parse_date_range_current_position():
    result = parse_date_range("Mar 2023 - Presente")
    assert result.start == date(2023, 3, 1)
    assert result.end is None


def test_parse_date_range_no_match_returns_none():
    assert parse_date_range("no dates here") is None
