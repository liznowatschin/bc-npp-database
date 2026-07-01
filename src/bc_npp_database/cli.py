"""Command-line interface for BC-NPPD."""

from __future__ import annotations

from pathlib import Path

import typer

from . import __version__
from .config import PROJECT_ABBREVIATION, PROJECT_NAME
from .validate import find_excluded_sources

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
