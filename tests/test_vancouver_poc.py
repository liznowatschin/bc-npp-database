from pathlib import Path

from bc_npp_database.vancouver_poc import (
    generate_vancouver_poc_list,
    migrate_legacy_species_id,
    validate_vancouver_poc_list,
)

WORKBOOK = Path("data/workbooks/native_plant_restoration_workbook_v1.0.0c.xlsx")
POC_DIR = Path("data/poc/vancouver")


def test_legacy_species_id_migration_is_deterministic():
    assert migrate_legacy_species_id("CDF-0001") == "BCNPPD-0001"
    assert migrate_legacy_species_id("CDF-0020") == "BCNPPD-0020"
    assert migrate_legacy_species_id("BCNPPD-0001") == "BCNPPD-0001"


def test_generate_vancouver_poc_list_from_workbook(tmp_path):
    result = generate_vancouver_poc_list(WORKBOOK, tmp_path / "poc")

    assert result.diagnostics == ()
    assert result.counts == {
        "plant_list": 20,
        "sources": 24,
        "source_attribution": 41,
    }
    assert (tmp_path / "poc" / "plant_list.csv").exists()


def test_tracked_vancouver_poc_artifact_validates_cleanly():
    result = validate_vancouver_poc_list(POC_DIR)

    assert result.diagnostics == ()
    assert result.counts["plant_list"] == 52
    assert result.counts["sources"] == 25
    assert result.counts["source_attribution"] == 73


def test_vancouver_poc_validator_reports_missing_files(tmp_path):
    result = validate_vancouver_poc_list(tmp_path)

    assert {diagnostic.code for diagnostic in result.diagnostics} == {"missing_poc_file"}


def test_vancouver_poc_validator_reports_link_errors(tmp_path):
    generate_vancouver_poc_list(WORKBOOK, tmp_path / "poc")
    attribution = tmp_path / "poc" / "source_attribution.csv"
    attribution.write_text(
        attribution.read_text(encoding="utf-8").replace("SRC-0001", "SRC-9999", 1),
        encoding="utf-8",
    )

    result = validate_vancouver_poc_list(tmp_path / "poc")

    assert any(diagnostic.code == "unknown_poc_source_id" for diagnostic in result.diagnostics)
