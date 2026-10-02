from ats_simulator.scoring.penalties import (
    apply_layout_penalty,
    apply_low_text_penalty,
    apply_table_penalty,
)


def test_apply_layout_penalty_reduces_score_when_multicolumn():
    assert apply_layout_penalty(100, multi_column_layout=True) == 85
    assert apply_layout_penalty(100, multi_column_layout=False) == 100


def test_apply_layout_penalty_floors_at_zero():
    assert apply_layout_penalty(10, multi_column_layout=True) == 0


def test_apply_table_penalty_reduces_score_when_tables_present():
    assert apply_table_penalty(100, has_tables=True) == 80
    assert apply_table_penalty(100, has_tables=False) == 100


def test_apply_table_penalty_floors_at_zero():
    assert apply_table_penalty(10, has_tables=True) == 0


def test_apply_low_text_penalty_caps_score():
    assert apply_low_text_penalty(100, low_text_content=True) == 5
    assert apply_low_text_penalty(100, low_text_content=False) == 100
    assert apply_low_text_penalty(2, low_text_content=True) == 2
