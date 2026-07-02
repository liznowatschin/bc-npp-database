import csv
import json
from pathlib import Path

from bc_npp_database.pollinators import (
    POLLINATOR_FIELDS,
    generate_vancouver_pollinator_module,
    has_error_diagnostics,
    validate_vancouver_pollinator_module,
)

USABILITY_DIR = Path("data/poc/vancouver/usability")
POLLINATOR_DIR = Path("data/poc/vancouver/pollinator_module")


def test_generate_vancouver_pollinator_module_from_tracked_usability(tmp_path):
    result = generate_vancouver_pollinator_module(USABILITY_DIR, tmp_path / "pollinators")

    assert not has_error_diagnostics(result.diagnostics)
    assert result.counts == {
        "pollinator_review": 53,
        "pollinator_evidence_gaps": 371,
        "pollinator_source_requirements": 7,
    }
    assert (tmp_path / "pollinators" / "pollinator_review.csv").exists()


def test_tracked_vancouver_pollinator_module_validates_cleanly():
    result = validate_vancouver_pollinator_module(POLLINATOR_DIR)

    assert result.diagnostics == ()
    assert result.counts["pollinator_review"] == 53
    assert result.counts["pollinator_evidence_gaps"] == 53 * len(POLLINATOR_FIELDS)


def test_pollinator_review_rows_keep_psi_not_ready():
    with (POLLINATOR_DIR / "pollinator_review.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert {row["review_status"] for row in rows} == {"review_queue"}
    assert {row["psi_readiness"] for row in rows} == {"not_ready"}
    assert all("not PSI scores" in row["evidence_caveat"] for row in rows)


def test_pollinator_gap_rows_are_unknown_and_need_review():
    with (POLLINATOR_DIR / "pollinator_evidence_gaps.csv").open(
        newline="",
        encoding="utf-8",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 371
    assert {row["current_value"] for row in rows} == {"Unknown"}
    assert {row["review_status"] for row in rows} == {"needs_review"}
    assert {row["pollinator_field"] for row in rows} == set(POLLINATOR_FIELDS)


def test_pollinator_validator_reports_missing_files(tmp_path):
    result = validate_vancouver_pollinator_module(tmp_path)

    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "missing_pollinator_file"
    }


def test_pollinator_validator_rejects_invalid_statuses(tmp_path):
    result = generate_vancouver_pollinator_module(USABILITY_DIR, tmp_path / "pollinators")
    assert not has_error_diagnostics(result.diagnostics)
    review_path = tmp_path / "pollinators" / "pollinator_review.csv"
    rows = list(csv.DictReader(review_path.open(newline="", encoding="utf-8")))
    rows[0]["psi_readiness"] = "ready"
    rows[0]["review_status"] = "review_queue"
    _write_csv(review_path, rows)

    validation = validate_vancouver_pollinator_module(tmp_path / "pollinators")

    assert "psi_ready_without_accepted_review" in {
        diagnostic.code for diagnostic in validation.diagnostics
    }


def test_pollinator_manifest_preserves_public_hygiene_flags():
    manifest = json.loads((POLLINATOR_DIR / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["status"] == "pollinator_review_scaffold"
    assert manifest["public_hygiene"] == {
        "external_downloads_required": False,
        "private_data_tracked": False,
        "raw_sources_tracked": False,
    }


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
