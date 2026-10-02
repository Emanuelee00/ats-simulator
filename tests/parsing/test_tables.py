from ats_simulator.parsing.tables import has_pdf_tables
from tests.fixtures import make_pdf, make_pdf_with_table


def test_has_pdf_tables_true_for_ruled_grid(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf_with_table(pdf_path)
    assert has_pdf_tables(pdf_path) is True


def test_has_pdf_tables_false_for_plain_text(tmp_path):
    pdf_path = tmp_path / "cv.pdf"
    make_pdf(pdf_path, ["Mario Rossi", "Experience", "Senior Developer"])
    assert has_pdf_tables(pdf_path) is False
