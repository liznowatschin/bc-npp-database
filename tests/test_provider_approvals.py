import csv
import shutil
from pathlib import Path

from bc_npp_database.provider_approvals import (
    APPROVAL_FIELDS,
    apply_provider_approval_sequence,
    apply_provider_approvals,
    validate_provider_approvals,
)

APPROVALS = Path("tests/fixtures/provider_approvals/approval_manifest.csv")
POC_DIR = Path("data/poc/vancouver")


def test_provider_approval_manifest_validates_cleanly():
    result = validate_provider_approvals(APPROVALS)

    assert result.counts["approval_manifest"] == 5
    assert result.diagnostics == ()


def test_apply_provider_approvals_imports_only_approved_rows(tmp_path):
    poc_dir = _clean_poc_dir(tmp_path)
    result = apply_provider_approvals(
        APPROVALS,
        poc_dir,
        tmp_path / "vancouver",
        regenerate_downstream=False,
    )

    assert not [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]
    assert result.counts["approved_rows"] == 4
    assert result.counts["supplier_availability"] == 1
    assert result.counts["mowability"] == 1

    plants = _read_csv(tmp_path / "vancouver" / "plant_list.csv")
    assert any(row["Botanical Name"] == "Festuca rubra" for row in plants)
    assert not any(row["Botanical Name"] == "Lactuca sativa" for row in plants)
    achillea = next(row for row in plants if row["Species ID"] == "BCNPPD-0001")
    assert achillea["Plant Type"] == "Forb"

    suppliers = _read_csv(tmp_path / "vancouver" / "provider_data" / "supplier_availability.csv")
    mowability = _read_csv(tmp_path / "vancouver" / "provider_data" / "mowability.csv")
    assert suppliers[0]["species_id"] == "BCNPPD-0001"
    assert suppliers[0]["supplier_status"] == "available"
    assert mowability[0]["mowability_score"] == "3"
    assert "does not make UNI, PSI, or RVI" in mowability[0]["caveat"]


def test_apply_provider_approvals_adds_source_attribution(tmp_path):
    poc_dir = _clean_poc_dir(tmp_path)
    result = apply_provider_approvals(
        APPROVALS,
        poc_dir,
        tmp_path / "vancouver",
        regenerate_downstream=False,
    )

    assert result.counts["source_attribution"] > 84
    attribution = _read_csv(tmp_path / "vancouver" / "source_attribution.csv")
    provider_attribution = [
        row for row in attribution if row["external_id"].startswith("provider_approval:")
    ]
    assert {row["claim_field"] for row in provider_attribution} >= {
        "Plant Type",
        "supplier_availability",
        "mowability_score",
        "provider_candidate",
    }


def test_apply_provider_approvals_carries_forward_existing_provider_data(tmp_path):
    poc_dir = _clean_poc_dir(tmp_path)
    rows = _read_csv(APPROVALS)
    satin_path = tmp_path / "satin.csv"
    premier_path = tmp_path / "premier.csv"
    _write_csv(satin_path, [row for row in rows if row["provider_id"] == "PROV-SATIN"])
    _write_csv(premier_path, [row for row in rows if row["provider_id"] == "PROV-PREMIER"])

    first = apply_provider_approvals(
        satin_path,
        poc_dir,
        tmp_path / "step1",
        regenerate_downstream=False,
    )
    second = apply_provider_approvals(
        premier_path,
        tmp_path / "step1",
        tmp_path / "step2",
        regenerate_downstream=False,
    )

    assert first.counts["approval_manifest"] == 3
    assert second.counts["approval_manifest"] == 4
    suppliers = _read_csv(tmp_path / "step2" / "provider_data" / "supplier_availability.csv")
    mowability = _read_csv(tmp_path / "step2" / "provider_data" / "mowability.csv")
    assert len(suppliers) == 1
    assert len(mowability) == 1
    plants = _read_csv(tmp_path / "step2" / "plant_list.csv")
    assert any(row["Botanical Name"] == "Festuca rubra" for row in plants)


def test_apply_provider_approval_sequence_cumulates_manifests(tmp_path):
    poc_dir = _clean_poc_dir(tmp_path)
    rows = _read_csv(APPROVALS)
    satin_path = tmp_path / "satin.csv"
    premier_path = tmp_path / "premier.csv"
    _write_csv(satin_path, [row for row in rows if row["provider_id"] == "PROV-SATIN"])
    _write_csv(premier_path, [row for row in rows if row["provider_id"] == "PROV-PREMIER"])

    result = apply_provider_approval_sequence(
        [satin_path, premier_path],
        poc_dir,
        tmp_path / "sequence",
        regenerate_downstream=False,
    )

    assert result.counts["approval_manifest"] == 4
    assert result.counts["supplier_availability"] == 1
    assert result.counts["mowability"] == 1
    plants = _read_csv(tmp_path / "sequence" / "plant_list.csv")
    assert any(row["Botanical Name"] == "Festuca rubra" for row in plants)


def test_apply_provider_approval_sequence_namespaces_colliding_approval_ids(tmp_path):
    poc_dir = _clean_poc_dir(tmp_path)
    rows = _read_csv(APPROVALS)
    satin_row = next(row for row in rows if row["provider_id"] == "PROV-SATIN")
    premier_row = next(row for row in rows if row["provider_id"] == "PROV-PREMIER")
    satin_row = {**satin_row, "approval_id": "PA-DRAFT-0001"}
    premier_row = {**premier_row, "approval_id": "PA-DRAFT-0001"}
    satin_path = tmp_path / "satin.csv"
    premier_path = tmp_path / "premier.csv"
    _write_csv(satin_path, [satin_row])
    _write_csv(premier_path, [premier_row])

    result = apply_provider_approval_sequence(
        [satin_path, premier_path],
        poc_dir,
        tmp_path / "sequence",
        regenerate_downstream=False,
    )

    assert not [diagnostic for diagnostic in result.diagnostics if diagnostic.severity == "error"]
    approval_rows = _read_csv(tmp_path / "sequence" / "provider_data" / "approval_manifest.csv")
    approval_ids = {row["approval_id"] for row in approval_rows}
    assert "PA-DRAFT-0001" in approval_ids
    assert "PROV-PREMIER-PA-DRAFT-0001" in approval_ids
    attribution = _read_csv(tmp_path / "sequence" / "provider_data" / "source_attribution.csv")
    external_ids = {row["external_id"] for row in attribution}
    assert "provider_approval:PROV-PREMIER-PA-DRAFT-0001" in external_ids


def test_provider_approval_validation_rejects_bad_status_and_mowability(tmp_path):
    path = tmp_path / "approval_manifest.csv"
    path.write_text(
        "approval_id,sandbox_table,provider_id,botanical_name,species_id,approval_status,"
        "target_action,source_url,mowability_score\n"
        "BAD-1,mowability.csv,PROV-SATIN,Achillea millefolium,BCNPPD-0001,approved,"
        "record_mowability,https://satinflower.ca/products/achillea-millefolium,9\n"
        "BAD-2,candidate_species.csv,PROV-NOPE,Festuca rubra,,banana,"
        "add_species,https://example.com,\n",
        encoding="utf-8",
    )

    result = validate_provider_approvals(path)
    codes = {diagnostic.code for diagnostic in result.diagnostics}
    assert "invalid_mowability_score" in codes
    assert "invalid_approval_status" in codes
    assert "unknown_provider_id" in codes


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=APPROVAL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _clean_poc_dir(tmp_path: Path) -> Path:
    destination = tmp_path / "clean_poc"
    shutil.copytree(POC_DIR, destination)
    provider_data = destination / "provider_data"
    if provider_data.exists():
        shutil.rmtree(provider_data)
    return destination
