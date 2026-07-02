import csv
from pathlib import Path

from bc_npp_database.evidence_hardening import (
    generate_vancouver_evidence_hardening,
    has_error_diagnostics,
    validate_vancouver_evidence_hardening,
)

POC_DIR = Path("data/poc/vancouver")
HARDENING_DIR = Path("data/poc/vancouver/evidence_hardening")


def test_generate_vancouver_evidence_hardening_from_tracked_poc(tmp_path):
    result = generate_vancouver_evidence_hardening(POC_DIR, tmp_path / "hardening")

    assert not has_error_diagnostics(result.diagnostics)
    assert result.counts == {
        "hardened_plant_list": 52,
        "reviewed_sources": 25,
        "reviewed_fields": 80,
        "evidence_gaps": 260,
        "score_readiness": 156,
    }
    assert (tmp_path / "hardening" / "reviewed_fields.csv").exists()


def test_tracked_vancouver_evidence_hardening_validates_cleanly():
    result = validate_vancouver_evidence_hardening(HARDENING_DIR)

    assert result.diagnostics == ()
    assert result.counts["hardened_plant_list"] == 52
    assert result.counts["reviewed_fields"] == 80
    assert result.counts["score_readiness"] == 156


def test_evidence_hardening_validator_reports_missing_files(tmp_path):
    result = validate_vancouver_evidence_hardening(tmp_path)

    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "missing_hardening_file"
    }


def test_score_readiness_remains_not_ready_for_tracked_artifact():
    with (HARDENING_DIR / "score_readiness.csv").open(newline="", encoding="utf-8") as handle:
        score_rows = list(csv.DictReader(handle))

    assert {row["readiness_status"] for row in score_rows} == {"not_ready"}
    assert all(
        "candidate display values and are not accepted P4 score inputs" in row["reason"]
        for row in score_rows
    )


def test_reviewed_fields_are_limited_to_identity_native_range_fields():
    reviewed_fields = (HARDENING_DIR / "reviewed_fields.csv").read_text(encoding="utf-8")

    assert "Botanical Name" in reviewed_fields
    assert "Native Status" in reviewed_fields
    assert "Urban Toughness" not in reviewed_fields
    assert "Soil Moisture" not in reviewed_fields
