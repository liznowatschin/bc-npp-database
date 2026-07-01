from typer.testing import CliRunner

from bc_npp_database.cli import app

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "bc-npp-database 0.1.0a0" in result.stdout


def test_cli_info():
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "BC Native Plant & Pollinator Database" in result.stdout
    assert "BC-NPPD" in result.stdout


def test_validate_source_policy_command_detects_excluded_url(tmp_path):
    source_file = tmp_path / "source.txt"
    source_file.write_text(
        "https://vancouver.ca/files/cov/vancouver-gri-planting-guidelines.pdf",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["validate-source-policy", str(source_file)])

    assert result.exit_code == 1
    assert "Excluded source found" in result.stderr
