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


def test_scrape_provider_sandbox_command_json(tmp_path):
    result = runner.invoke(
        app,
        [
            "scrape-provider-sandbox",
            "PROV-SATIN",
            "--input-dir",
            "tests/fixtures/providers",
            "--out-dir",
            str(tmp_path / "sandbox"),
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"candidate_species": 1' in result.stdout
    assert (tmp_path / "sandbox" / "candidate_species.csv").exists()


def test_build_provider_review_command_json(tmp_path):
    scrape_result = runner.invoke(
        app,
        [
            "scrape-provider-sandbox",
            "PROV-SATIN",
            "--input-dir",
            "tests/fixtures/providers",
            "--out-dir",
            str(tmp_path / "sandbox"),
            "--json",
        ],
    )
    assert scrape_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "build-provider-review",
            str(tmp_path / "sandbox"),
            "--out-dir",
            str(tmp_path / "review"),
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"candidate_species": 1' in result.stdout
    assert (tmp_path / "review" / "index.html").exists()


def test_build_provider_approval_review_command_json(tmp_path):
    scrape_result = runner.invoke(
        app,
        [
            "scrape-provider-sandbox",
            "PROV-SATIN",
            "--input-dir",
            "tests/fixtures/providers",
            "--out-dir",
            str(tmp_path / "sandbox"),
            "--json",
        ],
    )
    assert scrape_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "build-provider-approval-review",
            str(tmp_path / "sandbox"),
            "--poc-dir",
            "data/poc/vancouver",
            "--out-dir",
            str(tmp_path / "approval_review"),
            "--reviewer",
            "tester",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"review_items": 1' in result.stdout
    assert (tmp_path / "approval_review" / "index.html").exists()
    assert (tmp_path / "approval_review" / "approval_manifest_draft.csv").exists()


def test_generate_provider_source_workflow_command_json(tmp_path):
    workflow_path = tmp_path / "premier.yaml"
    result = runner.invoke(
        app,
        [
            "generate-provider-source-workflow",
            "PROV-PREMIER",
            "--out-path",
            str(workflow_path),
            "--reviewer",
            "tester",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"provider_id": "PROV-PREMIER"' in result.stdout
    text = workflow_path.read_text(encoding="utf-8")
    assert "provider: bc_npp_database.source_sweep" in text
    assert "provider_id: PROV-PREMIER" in text
    assert "reviewer: \"tester\"" in text


def test_generate_provider_source_workflow_has_defaults_for_all_requested_providers(tmp_path):
    expected = {
        "PROV-SATIN": "https://satinflower.ca/collections/seed",
        "PROV-NWM": "https://northwestmeadowscapes.com",
        "PROV-WCS": "https://www.westcoastseeds.com/collections/wildflower-seeds",
        "PROV-PREMIER": "https://premierpacificseeds.ca",
    }
    for provider_id, expected_url in expected.items():
        workflow_path = tmp_path / f"{provider_id}.yaml"
        result = runner.invoke(
            app,
            [
                "generate-provider-source-workflow",
                provider_id,
                "--out-path",
                str(workflow_path),
                "--json",
            ],
        )

        assert result.exit_code == 0
        assert expected_url in workflow_path.read_text(encoding="utf-8")


def test_generate_provider_source_workflow_rejects_unknown_provider(tmp_path):
    result = runner.invoke(
        app,
        [
            "generate-provider-source-workflow",
            "PROV-NOPE",
            "--out-path",
            str(tmp_path / "bad.yaml"),
            "--json",
        ],
    )

    assert result.exit_code == 1
    assert "provider_workflow.unknown_provider" in result.stdout


def test_validate_provider_approvals_command_json():
    result = runner.invoke(
        app,
        [
            "validate-provider-approvals",
            "tests/fixtures/provider_approvals/approval_manifest.csv",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"approval_manifest": 5' in result.stdout
    assert '"diagnostics": []' in result.stdout


def test_apply_provider_approvals_command_json(tmp_path):
    result = runner.invoke(
        app,
        [
            "apply-provider-approvals",
            "tests/fixtures/provider_approvals/approval_manifest.csv",
            "--poc-dir",
            "data/poc/vancouver",
            "--out-dir",
            str(tmp_path / "vancouver"),
            "--skip-regeneration",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"approved_rows": 4' in result.stdout
    assert (tmp_path / "vancouver" / "provider_data" / "supplier_availability.csv").exists()
    assert (tmp_path / "vancouver" / "provider_data" / "mowability.csv").exists()


def test_apply_provider_approval_sequence_command_json(tmp_path):
    result = runner.invoke(
        app,
        [
            "apply-provider-approval-sequence",
            "tests/fixtures/provider_approvals/approval_manifest.csv",
            "--poc-dir",
            "data/poc/vancouver",
            "--out-dir",
            str(tmp_path / "vancouver_sequence"),
            "--skip-regeneration",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"approved_rows": 4' in result.stdout
    assert (
        tmp_path / "vancouver_sequence" / "provider_data" / "supplier_availability.csv"
    ).exists()


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
