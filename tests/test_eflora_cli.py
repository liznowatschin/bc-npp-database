from pathlib import Path

from typer.testing import CliRunner

from bc_npp_database.cli import app

runner = CliRunner()


def test_resolve_eflora_species_command_json():
    result = runner.invoke(
        app,
        [
            "resolve-eflora-species",
            "Achillea millefolium",
            "--input-dir",
            "tests/fixtures/eflora",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"match_status": "exact"' in result.stdout
    assert "Achillea+millefolium" in result.stdout


def test_build_validate_and_apply_eflora_boost_commands_json(tmp_path):
    boost_dir = tmp_path / "boost"
    preview_dir = tmp_path / "preview"
    build_result = runner.invoke(
        app,
        [
            "build-eflora-boost",
            "tests/fixtures/eflora/species.csv",
            "--input-dir",
            "tests/fixtures/eflora",
            "--out-dir",
            str(boost_dir),
            "--access-date",
            "2026-07-03",
            "--json",
        ],
    )

    assert build_result.exit_code == 0
    assert '"resolved_species": 1' in build_result.stdout
    assert (boost_dir / "candidate_attributes.csv").exists()

    validate_result = runner.invoke(
        app,
        ["validate-eflora-boost", str(boost_dir), "--json"],
    )

    assert validate_result.exit_code == 0
    assert '"diagnostics": []' in validate_result.stdout

    apply_result = runner.invoke(
        app,
        [
            "apply-eflora-boost",
            str(boost_dir),
            "--poc-dir",
            "data/poc/vancouver",
            "--out-dir",
            str(preview_dir),
            "--json",
        ],
    )

    assert apply_result.exit_code == 0
    assert '"boost_attributes"' in apply_result.stdout
    assert (preview_dir / "eflora_boost" / "manifest.json").exists()


def test_eflora_workflow_example_uses_freshforge_provider_nodes():
    text = Path("examples/workflows/eflora_attribute_boost.yaml").read_text(encoding="utf-8")

    assert "provider: bc_npp_database.eflora.extract_boost" in text
    assert "provider: bc_npp_database.eflora.validate_boost" in text
    assert "provider: bc_npp_database.eflora.apply_preview" in text
    assert "command:" not in text
