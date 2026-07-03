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
from .evidence_hardening import (
    generate_vancouver_evidence_hardening,
    validate_vancouver_evidence_hardening,
)
from .evidence_hardening import (
    has_error_diagnostics as has_evidence_hardening_error_diagnostics,
)
from .foundation import (
    has_error_diagnostics as has_foundation_error_diagnostics,
)
from .foundation import (
    validate_foundation_dir,
)
from .pollinators import (
    generate_vancouver_pollinator_module,
    validate_vancouver_pollinator_module,
)
from .pollinators import (
    has_error_diagnostics as has_pollinator_error_diagnostics,
)
from .provider_approval_review import (
    build_provider_approval_review,
)
from .provider_approval_review import (
    has_error_diagnostics as has_provider_approval_review_error_diagnostics,
)
from .provider_approvals import (
    apply_provider_approvals,
    validate_provider_approvals,
)
from .provider_approvals import (
    has_error_diagnostics as has_provider_approval_error_diagnostics,
)
from .provider_scraping import (
    build_provider_review,
    scrape_provider_sandbox,
)
from .provider_scraping import (
    has_error_diagnostics as has_provider_scraping_error_diagnostics,
)
from .providers import (
    has_error_diagnostics as has_provider_error_diagnostics,
)
from .providers import (
    validate_provider_sandbox,
    validate_source_provider_file,
)
from .scoring import (
    calculate_scores,
    validate_score_inputs,
)
from .scoring import (
    has_error_diagnostics as has_score_error_diagnostics,
)
from .sources import (
    load_mapping_records,
    validate_source_attribution_records,
    validate_source_records,
)
from .usability import (
    generate_vancouver_usability,
    validate_vancouver_usability,
)
from .usability import (
    has_error_diagnostics as has_usability_error_diagnostics,
)
from .validate import find_excluded_sources
from .vancouver_poc import (
    generate_vancouver_poc_list,
    validate_vancouver_poc_list,
)
from .vancouver_poc import (
    has_error_diagnostics as has_vancouver_poc_error_diagnostics,
)
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


@app.command("validate-source-providers")
def validate_source_providers_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate source-provider registry records from CSV, JSON, or JSON Lines."""
    diagnostics = validate_source_provider_file(path)
    _emit_diagnostics(diagnostics, json_output=json_output)


@app.command("validate-provider-sandbox")
def validate_provider_sandbox_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate a provider sandbox directory."""
    result = validate_provider_sandbox(path)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    elif result.diagnostics:
        for diagnostic in result.diagnostics:
            typer.echo(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
    else:
        typer.echo(f"Provider sandbox validation passed for {path}.")
    if has_provider_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("scrape-provider-sandbox")
def scrape_provider_sandbox_command(
    provider_id: str,
    database_instance: str = typer.Option("vancouver", "--database-instance"),
    out_dir: Path = typer.Option(..., "--out-dir", help="Output provider sandbox directory."),
    input_dir: Path | None = typer.Option(
        None,
        "--input-dir",
        help="Directory of fixture or previously materialized provider HTML files.",
    ),
    live_fetch: bool = typer.Option(
        False,
        "--live-fetch",
        help="Fetch the provider homepage into ignored raw storage before parsing.",
    ),
    source_sweep: bool = typer.Option(
        False,
        "--source-sweep",
        help="Fetch supported provider catalogue feeds before parsing.",
    ),
    max_pages: int = typer.Option(
        5,
        "--max-pages",
        help="Maximum catalogue pages to fetch for source-sweep mode.",
    ),
    catalog_url: str | None = typer.Option(
        None,
        "--catalog-url",
        help="Provider collection or catalogue URL to use for source-sweep mode.",
    ),
    raw_dir: Path = typer.Option(
        Path("local/provider_raw"),
        "--raw-dir",
        help="Ignored directory for live-fetched raw provider HTML.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Generate a provider sandbox from fixture HTML or an optional live fetch."""
    result = scrape_provider_sandbox(
        provider_id,
        database_instance,
        out_dir,
        input_dir=input_dir,
        live_fetch=live_fetch,
        source_sweep=source_sweep,
        max_pages=max_pages,
        catalog_url=catalog_url,
        raw_dir=raw_dir,
    )
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        typer.echo(f"Generated provider sandbox at {out_dir}.")
        for name, path in result.paths.items():
            typer.echo(f"- {name}: {path}")
    if has_provider_scraping_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("build-provider-review")
def build_provider_review_command(
    sandbox_dir: Path,
    out_dir: Path = typer.Option(..., "--out-dir", help="Output provider review directory."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Build a static provider review page and CSV bundle."""
    result = build_provider_review(sandbox_dir, out_dir)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        typer.echo(f"Generated provider review bundle at {out_dir}.")
        for name, path in result.paths.items():
            typer.echo(f"- {name}: {path}")
    if has_provider_scraping_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("build-provider-approval-review")
def build_provider_approval_review_command(
    sandbox_dir: Path,
    poc_dir: Path = typer.Option(
        Path("data/poc/vancouver"),
        "--poc-dir",
        help="Vancouver PoC directory used for existing-species matching.",
    ),
    out_dir: Path = typer.Option(
        ...,
        "--out-dir",
        help="Output provider approval review directory.",
    ),
    reviewer: str = typer.Option("", "--reviewer", help="Reviewer name or role for draft rows."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Build a static expert approval app and draft approval manifest."""
    result = build_provider_approval_review(
        sandbox_dir,
        poc_dir,
        out_dir,
        reviewer=reviewer,
    )
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        typer.echo(f"Generated provider approval review app at {out_dir}.")
        for name, path in result.paths.items():
            typer.echo(f"- {name}: {path}")
    if has_provider_approval_review_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("validate-provider-approvals")
def validate_provider_approvals_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate a provider approval manifest or provider-data directory."""
    result = validate_provider_approvals(path)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    elif result.diagnostics:
        for diagnostic in result.diagnostics:
            typer.echo(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
    else:
        typer.echo(f"Provider approval validation passed for {path}.")
    if has_provider_approval_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("apply-provider-approvals")
def apply_provider_approvals_command(
    approvals_path: Path,
    poc_dir: Path = typer.Option(..., "--poc-dir", help="Input Vancouver PoC directory."),
    out_dir: Path = typer.Option(..., "--out-dir", help="Output Vancouver PoC directory."),
    skip_regeneration: bool = typer.Option(
        False,
        "--skip-regeneration",
        help="Do not regenerate evidence, usability, or pollinator artifacts.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Apply approved provider observations to the Vancouver PoC."""
    result = apply_provider_approvals(
        approvals_path,
        poc_dir,
        out_dir,
        regenerate_downstream=not skip_regeneration,
    )
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        typer.echo(f"Applied provider approvals to {out_dir}.")
        for name, path in result.paths.items():
            typer.echo(f"- {name}: {path}")
    if has_provider_approval_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


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


@app.command("validate-score-inputs")
def validate_score_inputs_command(
    path: Path,
    weights_path: Path | None = typer.Option(
        None,
        "--weights",
        help="Optional CSV, JSON, or JSON Lines score weights.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate score inputs and optional metric weights."""
    rows = load_mapping_records(path)
    weights = load_mapping_records(weights_path) if weights_path else []
    diagnostics = validate_score_inputs(rows, weights)
    _emit_diagnostics(diagnostics, json_output=json_output)


@app.command("calculate-scores")
def calculate_scores_command(
    path: Path,
    weights_path: Path | None = typer.Option(
        None,
        "--weights",
        help="Optional CSV, JSON, or JSON Lines score weights.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Calculate provisional scores from reviewed numeric score inputs."""
    rows = load_mapping_records(path)
    weights = load_mapping_records(weights_path) if weights_path else []
    result = calculate_scores(rows, weights)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        for score in result.results:
            value = "not calculated" if score.score is None else score.score
            typer.echo(f"{score.species_id} {score.score_family}: {value}")
        if result.diagnostics:
            typer.echo(f"Diagnostics: {len(result.diagnostics)}")
    if has_score_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("validate-foundation")
def validate_foundation_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate a BC-NPPD foundation artifact directory."""
    result = validate_foundation_dir(path)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    elif result.diagnostics:
        for diagnostic in result.diagnostics:
            typer.echo(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
    else:
        counts = result.to_summary_dict()["counts"]
        typer.echo(f"Foundation validation passed for {path}.")
        typer.echo(f"- species: {counts['species']}")
        typer.echo(f"- sources: {counts['sources']}")
        typer.echo(f"- source attribution: {counts['source_attribution']}")
        typer.echo(f"- score inputs: {counts['score_inputs']}")
    if has_foundation_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("generate-vancouver-poc-list")
def generate_vancouver_poc_list_command(
    workbook_path: Path,
    out_dir: Path = typer.Option(..., "--out-dir", help="Output directory for PoC artifacts."),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Generate the Vancouver plant list PoC artifact set."""
    result = generate_vancouver_poc_list(workbook_path, out_dir)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        typer.echo(f"Generated Vancouver PoC list at {out_dir}.")
        for name, path in result.paths.items():
            typer.echo(f"- {name}: {path}")
    if has_vancouver_poc_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("validate-vancouver-poc-list")
def validate_vancouver_poc_list_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate a generated Vancouver plant list PoC artifact directory."""
    result = validate_vancouver_poc_list(path)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    elif result.diagnostics:
        for diagnostic in result.diagnostics:
            typer.echo(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
    else:
        typer.echo(f"Vancouver PoC validation passed for {path}.")
    if has_vancouver_poc_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("harden-vancouver-evidence")
def harden_vancouver_evidence_command(
    poc_dir: Path,
    out_dir: Path = typer.Option(
        ...,
        "--out-dir",
        help="Output directory for evidence-hardening artifacts.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Generate P7 evidence-hardening artifacts for the Vancouver PoC list."""
    result = generate_vancouver_evidence_hardening(poc_dir, out_dir)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        typer.echo(f"Generated Vancouver evidence hardening at {out_dir}.")
        for name, path in result.paths.items():
            typer.echo(f"- {name}: {path}")
    if has_evidence_hardening_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("validate-vancouver-evidence")
def validate_vancouver_evidence_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate P7 Vancouver evidence-hardening artifacts."""
    result = validate_vancouver_evidence_hardening(path)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    elif result.diagnostics:
        for diagnostic in result.diagnostics:
            typer.echo(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
    else:
        typer.echo(f"Vancouver evidence hardening validation passed for {path}.")
    if has_evidence_hardening_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("generate-vancouver-usability")
def generate_vancouver_usability_command(
    hardening_dir: Path,
    out_dir: Path = typer.Option(
        ...,
        "--out-dir",
        help="Output directory for static usability artifacts.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Generate P8 static usability artifacts for the Vancouver PoC list."""
    result = generate_vancouver_usability(hardening_dir, out_dir)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        typer.echo(f"Generated Vancouver usability artifacts at {out_dir}.")
        for name, path in result.paths.items():
            typer.echo(f"- {name}: {path}")
    if has_usability_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("validate-vancouver-usability")
def validate_vancouver_usability_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate P8 Vancouver static usability artifacts."""
    result = validate_vancouver_usability(path)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    elif result.diagnostics:
        for diagnostic in result.diagnostics:
            typer.echo(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
    else:
        typer.echo(f"Vancouver usability validation passed for {path}.")
    if has_usability_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("generate-vancouver-pollinator-module")
def generate_vancouver_pollinator_module_command(
    usability_dir: Path,
    out_dir: Path = typer.Option(
        ...,
        "--out-dir",
        help="Output directory for pollinator review artifacts.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Generate pollinator evidence-review artifacts for the Vancouver PoC."""
    result = generate_vancouver_pollinator_module(usability_dir, out_dir)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    else:
        typer.echo(f"Generated Vancouver pollinator module artifacts at {out_dir}.")
        for name, path in result.paths.items():
            typer.echo(f"- {name}: {path}")
    if has_pollinator_error_diagnostics(result.diagnostics):
        raise typer.Exit(code=1)


@app.command("validate-vancouver-pollinator-module")
def validate_vancouver_pollinator_module_command(
    path: Path,
    json_output: bool = typer.Option(False, "--json", help="Emit JSON output."),
) -> None:
    """Validate Vancouver pollinator evidence-review artifacts."""
    result = validate_vancouver_pollinator_module(path)
    if json_output:
        typer.echo(json.dumps(result.to_summary_dict(), indent=2))
    elif result.diagnostics:
        for diagnostic in result.diagnostics:
            typer.echo(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
    else:
        typer.echo(f"Vancouver pollinator module validation passed for {path}.")
    if has_pollinator_error_diagnostics(result.diagnostics):
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
