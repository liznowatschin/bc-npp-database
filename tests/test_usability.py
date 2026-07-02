import csv
from pathlib import Path

from bc_npp_database.usability import (
    generate_vancouver_usability,
    has_error_diagnostics,
    validate_vancouver_usability,
)

HARDENING_DIR = Path("data/poc/vancouver/evidence_hardening")
USABILITY_DIR = Path("data/poc/vancouver/usability")


def test_generate_vancouver_usability_from_tracked_hardening(tmp_path):
    result = generate_vancouver_usability(HARDENING_DIR, tmp_path / "usability")

    assert not has_error_diagnostics(result.diagnostics)
    assert result.counts == {
        "plant_table": 20,
        "use_case_views": 61,
        "view_summary": 6,
    }
    assert (tmp_path / "usability" / "index.html").exists()


def test_tracked_vancouver_usability_validates_cleanly():
    result = validate_vancouver_usability(USABILITY_DIR)

    assert result.diagnostics == ()
    assert result.counts["plant_table"] == 20
    assert result.counts["view_summary"] == 6


def test_usability_validator_reports_missing_files(tmp_path):
    result = validate_vancouver_usability(tmp_path)

    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "missing_usability_file"
    }


def test_view_summary_preserves_candidate_and_insufficient_data_boundaries():
    with (USABILITY_DIR / "view_summary.csv").open(newline="", encoding="utf-8") as handle:
        rows = {row["use_case"]: row for row in csv.DictReader(handle)}

    assert rows["boulevard"]["candidate_count"] == "11"
    assert rows["pollinator_support"]["status"] == "review_queue"
    assert rows["pollinator_support"]["candidate_count"] == "20"
    assert rows["low_growing"]["status"] == "insufficient_data"
    assert rows["low_growing"]["candidate_count"] == "0"


def test_usability_rows_keep_score_readiness_and_caveats_visible():
    with (USABILITY_DIR / "plant_table.csv").open(newline="", encoding="utf-8") as handle:
        plant_rows = list(csv.DictReader(handle))
    with (USABILITY_DIR / "use_case_views.csv").open(newline="", encoding="utf-8") as handle:
        view_rows = list(csv.DictReader(handle))

    assert {row["score_readiness"] for row in plant_rows} == {"not_ready"}
    assert {row["score_readiness"] for row in view_rows} == {"not_ready"}
    assert all(row["poc_caveat"] for row in plant_rows)
    assert all(row["evidence_caveat"] for row in view_rows)


def test_static_html_is_self_contained_and_filterable():
    html = (USABILITY_DIR / "index.html").read_text(encoding="utf-8")

    assert "<table" in html
    assert "data-view=\"dry_sun\"" in html
    assert "http://" not in html
    assert "https://" not in html
