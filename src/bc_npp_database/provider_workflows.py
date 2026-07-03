"""FreshForge workflow authoring helpers for provider source review."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .diagnostics import Diagnostic, Severity
from .provider_scraping import PROVIDER_REGISTRY
from .sources import load_mapping_records

_PROVIDER_WORKFLOW_DEFAULTS = {
    "PROV-SATIN": {
        "catalog_url": "https://satinflower.ca/collections/seed",
        "max_pages": 5,
    },
    "PROV-NWM": {
        "catalog_url": "https://northwestmeadowscapes.com",
        "max_pages": 5,
    },
    "PROV-WCS": {
        "catalog_url": (
            "https://www.westcoastseeds.com/collections/wildflower-seeds,"
            "https://www.westcoastseeds.com/collections/lawn-solutions"
        ),
        "max_pages": 3,
    },
    "PROV-PREMIER": {
        "catalog_url": "https://premierpacificseeds.ca",
        "max_pages": 5,
    },
}


@dataclass(frozen=True)
class ProviderWorkflowResult:
    """Generated provider workflow summary."""

    path: str | None
    provider_id: str
    workflow_text: str
    diagnostics: tuple[Diagnostic, ...]

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "provider_id": self.provider_id,
            "workflow_text": self.workflow_text,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def generate_provider_source_workflow(
    provider_id: str,
    *,
    output_path: Path | None = None,
    catalog_url: str | None = None,
    max_pages: int | None = None,
    reviewer: str = "expert reviewer",
    database_instance: str = "vancouver",
    force: bool = False,
) -> ProviderWorkflowResult:
    """Generate a FreshForge YAML workflow for a provider source-review package."""
    diagnostics: list[Diagnostic] = []
    provider = _provider_record(provider_id)
    if provider is None:
        diagnostics.append(
            Diagnostic(
                code="provider_workflow.unknown_provider",
                message=f"Unknown provider ID: {provider_id}",
                field="provider_id",
                value=provider_id,
            )
        )
    if max_pages is not None and max_pages < 1:
        diagnostics.append(
            Diagnostic(
                code="provider_workflow.invalid_max_pages",
                message="max_pages must be a positive integer.",
                field="max_pages",
                value=str(max_pages),
            )
        )
    if output_path is not None and output_path.exists() and not force:
        diagnostics.append(
            Diagnostic(
                code="provider_workflow.output_exists",
                message="Output workflow already exists; pass --force to overwrite.",
                field="output_path",
                value=str(output_path),
            )
        )

    workflow_text = ""
    if not diagnostics:
        workflow_text = render_provider_source_workflow(
            provider_id,
            catalog_url=catalog_url or _default_catalog_url(provider_id, provider),
            max_pages=max_pages or _default_max_pages(provider_id),
            reviewer=reviewer,
            database_instance=database_instance,
        )
        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(workflow_text, encoding="utf-8")

    return ProviderWorkflowResult(
        path=str(output_path) if output_path is not None else None,
        provider_id=provider_id,
        workflow_text=workflow_text,
        diagnostics=tuple(diagnostics),
    )


def render_provider_source_workflow(
    provider_id: str,
    *,
    catalog_url: str,
    max_pages: int,
    reviewer: str,
    database_instance: str,
) -> str:
    """Render a FreshForge provider source-review workflow YAML string."""
    workflow_id = _workflow_id(provider_id)
    provider_label = provider_id.removeprefix("PROV-").lower()
    sandbox_dir = f"outputs/provider_sandbox_source_sweep/{provider_id}"
    review_dir = f"outputs/provider_review_source_sweep/{provider_id}"
    approval_review_dir = f"outputs/provider_approval_review/{provider_id}"
    return f"""workflow:
  id: {workflow_id}
  name: {_yaml_string(provider_label + " provider source-review package")}
  description: {_yaml_string("Sweep " + provider_id + " into BC-NPPD review artifacts.")}

nodes:
  - id: source_sweep
    provider: bc_npp_database.source_sweep
    parameters:
      provider_id: {provider_id}
      database_instance: {database_instance}
      live_fetch: true
      source_sweep: true
      catalog_url: {_yaml_string(catalog_url)}
      max_pages: {max_pages}
      raw_dir: local/provider_raw
    outputs:
      sandbox_dir: {sandbox_dir}
    artifacts:
      sandbox_dir: {sandbox_dir}

  - id: validate_sandbox
    provider: bc_npp_database.validate_sandbox
    needs:
      - source_sweep
    inputs:
      sandbox_dir: {sandbox_dir}

  - id: build_review
    provider: bc_npp_database.build_review
    needs:
      - validate_sandbox
    inputs:
      sandbox_dir: {sandbox_dir}
    outputs:
      review_dir: {review_dir}
    artifacts:
      review_dir: {review_dir}

  - id: build_approval_review
    provider: bc_npp_database.build_approval_review
    needs:
      - build_review
    inputs:
      sandbox_dir: {sandbox_dir}
      poc_dir: data/poc/vancouver
    parameters:
      reviewer: {_yaml_string(reviewer)}
    outputs:
      approval_review_dir: {approval_review_dir}
    artifacts:
      approval_review_dir: {approval_review_dir}
"""


def has_error_diagnostics(diagnostics: tuple[Diagnostic, ...] | list[Diagnostic]) -> bool:
    """Return whether diagnostics include an error."""
    return any(diagnostic.severity == Severity.ERROR for diagnostic in diagnostics)


def _provider_record(provider_id: str) -> dict[str, object] | None:
    for row in load_mapping_records(PROVIDER_REGISTRY):
        if row.get("provider_id") == provider_id:
            return row
    return None


def _default_catalog_url(provider_id: str, provider: dict[str, object] | None) -> str:
    if provider_id in _PROVIDER_WORKFLOW_DEFAULTS:
        return _PROVIDER_WORKFLOW_DEFAULTS[provider_id]["catalog_url"]
    if provider and provider.get("homepage_url"):
        return str(provider["homepage_url"]).rstrip("/")
    return ""


def _default_max_pages(provider_id: str) -> int:
    if provider_id in _PROVIDER_WORKFLOW_DEFAULTS:
        return int(_PROVIDER_WORKFLOW_DEFAULTS[provider_id]["max_pages"])
    return 5


def _workflow_id(provider_id: str) -> str:
    return f"provider_source_review_{provider_id.removeprefix('PROV-').lower()}"


def _yaml_string(value: str) -> str:
    return json.dumps(value)
