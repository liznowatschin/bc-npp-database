"""Command-line interface for BC-NPPD."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from . import __version__
from .canonical import (
    export_canonical_tables,
    has_error_diagnostics,
    import_canonical_workbook,
)
from .config import PROJECT_ABBREVIATION, PROJECT_NAME
from .sources import (
    load_mapping_records,
    validate_source_attribution_records,
    validate_source_records,
)
from .validate import find_excluded_sources
from .workbooks import inventory_workbook, validate_workbook

app = typer.Typer(help="BC Native Plant & Pollinator Database tools.", no_args_is_help=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"bc-npp-database {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the package version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """BC-NPPD command group."""


@app.command()
def info() -> None:
    """Print basic project information."""
    typer.echo(PROJECT_NAME)
    typer.echo(f"Abbreviation: {PROJECT_ABBREVIATION}")
    typer.echo(f"Version: {__version__}")


@app.command("validate-source-policy")
def validate_source_policy(path: Path) -> None:
    """Check a text-like file for explicitly excluded source URLs."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    violations = find_excluded_sources([{"path": str(path), "content": text}])
    if violations:
        for violation in violations:
            typer.echo(
                f"Excluded source found in {path}: {violation['excluded_url']}",
                err=True,
            )
        raise typer.Exit(code=1)
    typer.echo(f"No excluded sources found in {path}.")


@app.command("validate-source-records")
def validate_source_records_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate source/reference records from CSV, JSON, or JSON Lines."""
    diagnostics = validate_source_records(load_mapping_records(path))
    _emit_diagnostics(diagnostics, json_output=json_output)


@app.command("validate-source-attribution")
def validate_source_attribution_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate source attribution records from CSV, JSON, or JSON Lines."""
    diagnostics = validate_source_attribution_records(load_mapping_records(path))
    _emit_diagnostics(diagnostics, json_output=json_output)


@app.command("inventory-workbook")
def inventory_workbook_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Print a read-only workbook sheet inventory."""
    inventory = inventory_workbook(path)
    if json_output:
        typer.echo(json.dumps(inventory.to_dict(), indent=2))
        return
    typer.echo(f"Workbook: {inventory.path}")
    for sheet in inventory.sheets:
        headers = ", ".join(header for header in sheet.headers if header)
        rows = sheet.max_row if sheet.max_row is not None else "unknown"
        columns = sheet.max_column if sheet.max_column is not None else "unknown"
        typer.echo(f"- {sheet.name}: {rows} rows x {columns} columns")
        if headers:
            typer.echo(f"  headers: {headers}")


@app.command("validate-workbook")
def validate_workbook_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate workbook readability and expected foundation sheets."""
    diagnostics = validate_workbook(path)
    if json_output:
        typer.echo(json.dumps([diagnostic.to_dict() for diagnostic in diagnostics], indent=2))
    elif diagnostics:
        for diagnostic in diagnostics:
            typer.echo(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
    else:
        typer.echo(f"Workbook validation passed for {path}.")
    if any(diagnostic.severity.value == "error" for diagnostic in diagnostics):
        raise typer.Exit(code=1)


@app.command("import-canonical-workbook")
def import_canonical_workbook_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Import approved workbook sheets into canonical in-memory tables."""
    result = import_canonical_workbook(path)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        counts = result.to_summary_dict()["counts"]
        typer.echo(f"Imported canonical workbook: {path}")
        typer.echo(f"- species: {counts['species']}")
        typer.echo(f"- lookups: {counts['lookups']}")
        typer.echo(f"- source attribution: {counts['source_attribution']}")
        typer.echo(f"- bloom calendar: {counts['bloom_calendar']}")
        typer.echo(f"- diagnostics: {counts['diagnostics']}")
    if has_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("export-canonical-workbook")
def export_canonical_workbook_command(
    path: Path,
    out_dir: Path = typer.Option(..., "--out-dir", help="Output directory for CSV tables."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Import approved workbook sheets and export deterministic CSV tables."""
    import_result = import_canonical_workbook(path)
    export_result = export_canonical_tables(import_result, out_dir)
    if json_output:
        summary = import_result.to_summary_dict()
        summary["export"] = export_result.to_summary_dict()
        typer.echo(json.dumps(summary, indent=2))
    else:
        typer.echo(f"Exported canonical workbook tables to {out_dir}.")
        for table, exported_path in export_result.paths.items():
            typer.echo(f"- {table}: {exported_path}")
    if has_error_diagnostics(export_result.diagnostics):
        raise typer.Exit(code=1)


def _emit_diagnostics(diagnostics: list[object], *, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps([diagnostic.to_dict() for diagnostic in diagnostics], indent=2))
    elif diagnostics:
        for diagnostic in diagnostics:
            typer.echo(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
    else:
        typer.echo("Validation passed.")
    if any(diagnostic.severity.value == "error" for diagnostic in diagnostics):
        raise typer.Exit(code=1)
