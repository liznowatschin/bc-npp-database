import csv
import json
import shutil
from pathlib import Path

from bc_npp_database.diagnostics import Severity
from bc_npp_database.provider_approvals import (
    ProviderApprovalResult,
    apply_provider_sandbox,
    apply_provider_sandbox_sequence,
    auto_import_provider_sandboxes,
)
from bc_npp_database.providers import (
    SourceProviderRecord,
    validate_provider_sandbox,
    validate_source_provider_file,
    validate_source_provider_records,
)

REGISTRY = Path("data/source_providers/provider_registry.csv")
POC_DIR = Path("data/poc/vancouver")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def test_provider_registry_validates_cleanly():
    diagnostics = validate_source_provider_file(REGISTRY)

    assert diagnostics == []


def test_source_provider_record_round_trips_from_mapping():
    record = SourceProviderRecord.from_mapping(
        {
            "Provider ID": "PROV-SATIN",
            "Provider Name": "Satinflower Nurseries",
            "Homepage URL": "https://satinflower.ca",
            "Source Tier": "Tier 3",
            "In Scope Notes": "Native seed supplier context.",
            "Exclusion Notes": "Not sole authority for ecological scoring.",
            "Scrape Policy": "Polite fixture-backed fetches only in CI.",
        }
    )

    assert record.provider_id == "PROV-SATIN"
    assert record.to_dict()["source_tier"] == "Tier 3"


def test_provider_validation_checks_id_url_tier_and_duplicates():
    diagnostics = validate_source_provider_records(
        [
            {
                "provider_id": "PROV-SATIN",
                "provider_name": "Satinflower",
                "homepage_url": "https://satinflower.ca",
                "source_tier": "Tier 2",
                "in_scope_notes": "Native seed supplier context.",
                "exclusion_notes": "Not sole authority.",
                "scrape_policy": "Polite fetches.",
            },
            {
                "provider_id": "bad-id",
                "provider_name": "Duplicate",
                "homepage_url": "not-a-url",
                "source_tier": "Tier 9",
                "in_scope_notes": "Native seed supplier context.",
                "exclusion_notes": "Not sole authority.",
                "scrape_policy": "Polite fetches.",
            },
            {
                "provider_id": "PROV-SATIN",
                "provider_name": "Duplicate",
                "homepage_url": "https://example.com",
                "source_tier": "Tier 3",
                "in_scope_notes": "Native seed supplier context.",
                "exclusion_notes": "Not sole authority.",
                "scrape_policy": "Polite fetches.",
            },
        ]
    )

    codes = {diagnostic.code for diagnostic in diagnostics}
    assert {
        "provider_not_tier_3",
        "invalid_provider_id",
        "invalid_provider_url",
        "invalid_source_tier",
        "duplicate_provider_id",
    } <= codes


def test_provider_sandbox_validates_cleanly(tmp_path):
    sandbox = _write_provider_sandbox(tmp_path)

    result = validate_provider_sandbox(sandbox)

    assert result.diagnostics == ()
    assert result.counts["candidate_species"] == 1
    assert result.counts["mowability"] == 1


def test_provider_sandbox_flags_wcs_vegetables(tmp_path):
    sandbox = _write_provider_sandbox(
        tmp_path,
        species_overrides={
            "provider_id": "PROV-WCS",
            "product_category": "Vegetable Seeds",
        },
    )

    result = validate_provider_sandbox(sandbox)

    assert any(diagnostic.code == "wcs_vegetable_excluded" for diagnostic in result.diagnostics)


def test_provider_sandbox_warns_when_nwm_is_directly_eligible(tmp_path):
    sandbox = _write_provider_sandbox(
        tmp_path,
        species_overrides={
            "provider_id": "PROV-NWM",
            "vancouver_eligibility_status": "eligible",
        },
    )

    result = validate_provider_sandbox(sandbox)

    assert any(
        diagnostic.code == "nwm_requires_northward_review" for diagnostic in result.diagnostics
    )


def test_provider_sandbox_rejects_invalid_mowability_score(tmp_path):
    sandbox = _write_provider_sandbox(tmp_path, mowability_overrides={"mowability_score": "9"})

    result = validate_provider_sandbox(sandbox)

    assert any(diagnostic.code == "invalid_mowability_score" for diagnostic in result.diagnostics)


def _write_provider_sandbox(
    tmp_path,
    *,
    species_overrides: dict[str, str] | None = None,
    mowability_overrides: dict[str, str] | None = None,
) -> Path:
    sandbox = tmp_path / "provider_sandbox"
    sandbox.mkdir(parents=True)
    species_row = {
        "provider_id": "PROV-SATIN",
        "botanical_name": "Achillea millefolium",
        "common_name": "Common Yarrow",
        "candidate_status": "candidate",
        "vancouver_eligibility_status": "candidate",
        "source_url": "https://satinflower.ca/products/achillea-millefolium",
        "review_status": "pending_review",
        "product_category": "Native Seed",
        "notes": "",
    } | (species_overrides or {})
    mowability_row = {
        "provider_id": species_row["provider_id"],
        "botanical_name": species_row["botanical_name"],
        "mowability_score": "3",
        "source_url": species_row["source_url"],
        "review_status": "pending_review",
        "notes": "Candidate establishment-period mowing observation.",
    } | (mowability_overrides or {})
    _write_csv(
        sandbox / "inventory_pages.csv",
        [
            {
                "provider_id": species_row["provider_id"],
                "page_url": species_row["source_url"],
                "page_type": "product",
                "fetch_status": "fixture",
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(sandbox / "candidate_species.csv", [species_row])
    _write_csv(
        sandbox / "candidate_attributes.csv",
        [
            {
                "provider_id": species_row["provider_id"],
                "botanical_name": species_row["botanical_name"],
                "attribute_name": "supplier_note",
                "attribute_value": "Native seed product page.",
                "evidence_confidence": "Pending review",
                "source_url": species_row["source_url"],
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(
        sandbox / "supplier_availability.csv",
        [
            {
                "provider_id": species_row["provider_id"],
                "botanical_name": species_row["botanical_name"],
                "supplier_status": "available",
                "product_url": species_row["source_url"],
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(sandbox / "mowability.csv", [mowability_row])
    _write_csv(
        sandbox / "diagnostics.csv",
        [{"severity": "info", "code": "fixture", "message": "Synthetic fixture."}],
    )
    (sandbox / "manifest.json").write_text(
        json.dumps(
            {
                "database_instance": "vancouver",
                "provider_ids": [species_row["provider_id"]],
                "inventory_page_count": 1,
                "candidate_species_count": 1,
                "candidate_attribute_count": 1,
                "supplier_availability_count": 1,
                "mowability_count": 1,
                "public_hygiene": {
                    "raw_provider_html_tracked": False,
                    "external_downloads_required": False,
                    "private_data_tracked": False,
                },
            }
        ),
        encoding="utf-8",
    )
    return sandbox


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_apply_provider_sandbox_basic_auto_approve(tmp_path):
    """Test basic auto-approve of a sandbox with eligible candidates."""
    sandbox = _write_provider_sandbox(tmp_path)
    poc_dir = _clean_poc_dir(tmp_path)

    output_dir = tmp_path / "test_output" / "vancouver"

    result = apply_provider_sandbox(
        sandbox,
        poc_dir,
        output_dir,
        regenerate_downstream=False,
    )

    assert isinstance(result, ProviderApprovalResult)
    assert not [d for d in result.diagnostics if d.severity == Severity.ERROR]
    assert result.counts["eligible_species"] == 1
    assert result.counts["excluded_species"] == 0
    assert result.counts["approved_rows"] == 4  # species + supplier + attribute + mowability
    assert result.counts["supplier_included"] == 1
    assert result.counts["attribute_included"] == 1
    assert result.counts["mowability_included"] == 1

    approval_rows = _read_csv(output_dir / "provider_data" / "approval_manifest.csv")
    assert {row["approval_status"] for row in approval_rows} == {"approved"}
    assert {row["sandbox_table"] for row in approval_rows} == {
        "candidate_species.csv",
        "supplier_availability.csv",
        "candidate_attributes.csv",
        "mowability.csv",
    }

    plants = _read_csv(output_dir / "plant_list.csv")
    # The sandbox species already exists in POC, so we check it's present with our data
    assert any(row["Botanical Name"] == "Achillea millefolium" for row in plants)

    suppliers = _read_csv(output_dir / "provider_data" / "supplier_availability.csv")
    # Check that at least one supplier row has our provider_id
    assert any(supplier["provider_id"] == "PROV-SATIN" and
               supplier["botanical_name"] == "Achillea millefolium"
               for supplier in suppliers)

    mowability = _read_csv(output_dir / "provider_data" / "mowability.csv")
    assert any(m["provider_id"] == "PROV-SATIN" and
               m["botanical_name"] == "Achillea millefolium"
               for m in mowability)


def test_apply_provider_sandbox_excludes_ineligible_species(tmp_path):
    """Test that excluded species are filtered out."""
    sandbox = _write_provider_sandbox(
        tmp_path,
        species_overrides={
            "vancouver_eligibility_status": "excluded",
        },
    )
    poc_dir = _clean_poc_dir(tmp_path)

    output_dir = tmp_path / "test_output" / "vancouver"

    result = apply_provider_sandbox(
        sandbox,
        poc_dir,
        output_dir,
        regenerate_downstream=False,
    )

    assert isinstance(result, ProviderApprovalResult)
    assert not [d for d in result.diagnostics if d.severity == Severity.ERROR]
    assert result.counts["eligible_species"] == 0
    assert result.counts["excluded_species"] == 1
    assert result.counts["approved_rows"] == 0
    assert result.counts["supplier_included"] == 0
    assert result.counts["attribute_included"] == 0
    assert result.counts["mowability_included"] == 0

    # Check that no new supplier/mowability rows were added for our sandbox species
    suppliers = _read_csv(output_dir / "provider_data" / "supplier_availability.csv")
    mowability = _read_csv(output_dir / "provider_data" / "mowability.csv")
    assert not any(s["provider_id"] == "PROV-SATIN" for s in suppliers)
    assert not any(m["provider_id"] == "PROV-SATIN" for m in mowability)


def test_apply_provider_sandbox_wcs_vegetables_excluded(tmp_path):
    """Test that PROV-WCS vegetables are excluded."""
    sandbox = _write_provider_sandbox(
        tmp_path,
        species_overrides={
            "provider_id": "PROV-WCS",
            "botanical_name": "Lactuca sativa",
            "common_name": "Lettuce",
            "product_category": "Vegetable Seeds",
            "vancouver_eligibility_status": "excluded",
            "candidate_status": "excluded",
            "source_url": "https://westcoastseeds.com/products/lettuce",
        },
        mowability_overrides={
            "provider_id": "PROV-WCS",
            "botanical_name": "Lactuca sativa",
            "source_url": "https://westcoastseeds.com/products/lettuce",
        },
    )
    poc_dir = _clean_poc_dir(tmp_path)

    result = apply_provider_sandbox(
        sandbox,
        poc_dir,
        tmp_path / "vancouver",
        regenerate_downstream=False,
    )

    assert isinstance(result, ProviderApprovalResult)
    assert not [d for d in result.diagnostics if d.severity == Severity.ERROR]
    assert result.counts["eligible_species"] == 0
    assert result.counts["excluded_species"] == 1

    plants = _read_csv(tmp_path / "vancouver" / "plant_list.csv")
    assert not any(row["Botanical Name"] == "Lactuca sativa" for row in plants)


def test_apply_provider_sandbox_sequence_cumulates_sandboxes(tmp_path):
    satin = _write_provider_sandbox(tmp_path / "satin")
    premier = _write_provider_sandbox(
        tmp_path / "premier",
        species_overrides={
            "provider_id": "PROV-PREMIER",
            "botanical_name": "Festuca rubra",
            "common_name": "red fescue",
            "source_url": "https://premierpacificseeds.ca/products/festuca-rubra",
        },
        mowability_overrides={
            "provider_id": "PROV-PREMIER",
            "botanical_name": "Festuca rubra",
            "source_url": "https://premierpacificseeds.ca/products/festuca-rubra",
        },
    )
    poc_dir = _clean_poc_dir(tmp_path)

    result = apply_provider_sandbox_sequence(
        [satin, premier],
        poc_dir,
        tmp_path / "sequence",
        regenerate_downstream=False,
    )

    assert not [d for d in result.diagnostics if d.severity == Severity.ERROR]
    plants = _read_csv(tmp_path / "sequence" / "plant_list.csv")
    assert any(row["Botanical Name"] == "Achillea millefolium" for row in plants)
    assert any(row["Botanical Name"] == "Festuca rubra" for row in plants)
    suppliers = _read_csv(tmp_path / "sequence" / "provider_data" / "supplier_availability.csv")
    assert {row["provider_id"] for row in suppliers} >= {"PROV-SATIN", "PROV-PREMIER"}


def test_auto_import_provider_sandboxes_from_fixtures_for_other_providers(tmp_path):
    poc_dir = _clean_poc_dir(tmp_path)

    result = auto_import_provider_sandboxes(
        ["PROV-NWM", "PROV-WCS", "PROV-PREMIER"],
        poc_dir,
        tmp_path / "auto_import",
        sandbox_root=tmp_path / "sandboxes",
        input_dir=Path("tests/fixtures/providers"),
        regenerate_downstream=False,
    )

    assert not [d for d in result.diagnostics if d.severity == Severity.ERROR]
    assert result.counts["PROV-NWM_candidate_species"] == 1
    assert result.counts["PROV-WCS_candidate_species"] == 2
    assert result.counts["PROV-PREMIER_candidate_species"] == 1
    assert result.counts["sequence_sandbox_species"] == 4
    assert result.counts["sequence_eligible_species"] == 3
    assert result.counts["sequence_excluded_species"] == 1
    assert result.counts["sequence_supplier_included"] == 3
    assert result.counts["sequence_attribute_included"] == 4
    assert result.counts["sequence_mowability_included"] == 2

    approval_rows = _read_csv(tmp_path / "auto_import" / "provider_data" / "approval_manifest.csv")
    assert {row["approval_status"] for row in approval_rows} == {"approved"}
    assert {row["sandbox_table"] for row in approval_rows} == {
        "candidate_species.csv",
        "supplier_availability.csv",
        "candidate_attributes.csv",
        "mowability.csv",
    }
    assert {row["provider_id"] for row in approval_rows} == {
        "PROV-NWM",
        "PROV-WCS",
        "PROV-PREMIER",
    }

    plants = _read_csv(tmp_path / "auto_import" / "plant_list.csv")
    candidate_species = _read_csv(
        tmp_path / "auto_import" / "provider_data" / "candidate_species.csv"
    )
    candidate_attributes = _read_csv(
        tmp_path / "auto_import" / "provider_data" / "candidate_attributes.csv"
    )
    suppliers = _read_csv(
        tmp_path / "auto_import" / "provider_data" / "supplier_availability.csv"
    )
    assert {row["provider_id"] for row in candidate_species} == {
        "PROV-NWM",
        "PROV-WCS",
        "PROV-PREMIER",
    }
    assert {row["provider_id"] for row in candidate_attributes} == {
        "PROV-NWM",
        "PROV-WCS",
        "PROV-PREMIER",
    }
    assert {row["provider_id"] for row in suppliers} >= {
        "PROV-NWM",
        "PROV-WCS",
        "PROV-PREMIER",
    }
    assert len(plants) >= 3


def _clean_poc_dir(tmp_path: Path) -> Path:
    destination = tmp_path / "clean_poc"
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(POC_DIR, destination)
    provider_data = destination / "provider_data"
    if provider_data.exists():
        shutil.rmtree(provider_data)
    return destination
