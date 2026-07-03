import csv
from pathlib import Path

from bc_npp_database.provider_approvals import (
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
    result = apply_provider_approvals(
        APPROVALS,
        POC_DIR,
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
    result = apply_provider_approvals(
        APPROVALS,
        POC_DIR,
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
