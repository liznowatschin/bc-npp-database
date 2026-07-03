import csv
import json
from pathlib import Path

from bc_npp_database.providers import (
    SourceProviderRecord,
    validate_provider_sandbox,
    validate_source_provider_file,
    validate_source_provider_records,
)

REGISTRY = Path("data/source_providers/provider_registry.csv")


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
    sandbox.mkdir()
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
        "botanical_name": "Achillea millefolium",
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
                "botanical_name": "Achillea millefolium",
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
                "botanical_name": "Achillea millefolium",
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
