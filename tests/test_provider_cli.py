import csv
import json
from pathlib import Path

from typer.testing import CliRunner

from bc_npp_database.cli import app

runner = CliRunner()


def test_validate_source_providers_command_json():
    result = runner.invoke(
        app,
        ["validate-source-providers", "data/source_providers/provider_registry.csv", "--json"],
    )

    assert result.exit_code == 0
    assert result.stdout.strip() == "[]"


def test_validate_source_providers_command_reports_errors(tmp_path):
    path = tmp_path / "providers.csv"
    path.write_text(
        "provider_id,provider_name,homepage_url,source_tier,in_scope_notes,exclusion_notes,scrape_policy\n"
        "BAD,Provider,not-a-url,Tier 9,In scope,Exclusions,Policy\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["validate-source-providers", str(path), "--json"])

    assert result.exit_code == 1
    assert "invalid_provider_id" in result.stdout
    assert "invalid_provider_url" in result.stdout


def test_validate_provider_sandbox_command_json(tmp_path):
    sandbox = _write_minimal_sandbox(tmp_path)

    result = runner.invoke(app, ["validate-provider-sandbox", str(sandbox), "--json"])

    assert result.exit_code == 0
    assert '"candidate_species": 1' in result.stdout
    assert '"diagnostics": []' in result.stdout


def _write_minimal_sandbox(tmp_path) -> Path:
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    source_url = "https://premierpacificseeds.ca/products/"
    _write_csv(
        sandbox / "inventory_pages.csv",
        [
            {
                "provider_id": "PROV-PREMIER",
                "page_url": source_url,
                "page_type": "collection",
                "fetch_status": "fixture",
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(
        sandbox / "candidate_species.csv",
        [
            {
                "provider_id": "PROV-PREMIER",
                "botanical_name": "Festuca rubra",
                "candidate_status": "candidate",
                "vancouver_eligibility_status": "needs_review",
                "source_url": source_url,
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(
        sandbox / "candidate_attributes.csv",
        [
            {
                "provider_id": "PROV-PREMIER",
                "botanical_name": "Festuca rubra",
                "attribute_name": "supplier_category",
                "attribute_value": "BC native grasses and forbs",
                "evidence_confidence": "Pending review",
                "source_url": source_url,
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(
        sandbox / "supplier_availability.csv",
        [
            {
                "provider_id": "PROV-PREMIER",
                "botanical_name": "Festuca rubra",
                "supplier_status": "mix_component",
                "product_url": source_url,
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(
        sandbox / "mowability.csv",
        [
            {
                "provider_id": "PROV-PREMIER",
                "botanical_name": "Festuca rubra",
                "mowability_score": "4",
                "source_url": source_url,
                "review_status": "pending_review",
            }
        ],
    )
    _write_csv(
        sandbox / "diagnostics.csv",
        [{"severity": "info", "code": "fixture", "message": "Synthetic fixture."}],
    )
    (sandbox / "manifest.json").write_text(
        json.dumps(
            {
                "database_instance": "vancouver",
                "provider_ids": ["PROV-PREMIER"],
                "inventory_page_count": 1,
                "candidate_species_count": 1,
                "candidate_attribute_count": 1,
                "supplier_availability_count": 1,
                "mowability_count": 1,
                "public_hygiene": {"raw_provider_html_tracked": False},
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
