from pathlib import Path

from bc_npp_database.foundation import validate_foundation_dir

FOUNDATION_DIR = Path("data/foundation/v1.0.0a")


def test_foundation_artifacts_validate_cleanly():
    result = validate_foundation_dir(FOUNDATION_DIR)

    assert result.diagnostics == ()
    assert result.counts == {
        "species": 1,
        "sources": 2,
        "source_attribution": 8,
        "score_inputs": 3,
    }


def test_foundation_validator_reports_missing_files(tmp_path):
    result = validate_foundation_dir(tmp_path)

    codes = {diagnostic.code for diagnostic in result.diagnostics}
    assert codes == {"missing_foundation_file"}


def test_foundation_validator_reports_cross_file_mismatch(tmp_path):
    source_dir = FOUNDATION_DIR
    for path in source_dir.iterdir():
        target = tmp_path / path.name
        target.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    species_path = tmp_path / "species.csv"
    species_path.write_text(
        species_path.read_text(encoding="utf-8").replace("BCNPPD-0001", "BCNPPD-9999", 1),
        encoding="utf-8",
    )

    result = validate_foundation_dir(tmp_path)

    assert any(
        diagnostic.code == "foundation_species_mismatch" for diagnostic in result.diagnostics
    )
