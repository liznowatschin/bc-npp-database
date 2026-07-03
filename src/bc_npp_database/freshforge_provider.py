"""FreshForge provider adapter for BC-NPPD workflows."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .provider_approval_review import build_provider_approval_review
from .provider_scraping import build_provider_review, scrape_provider_sandbox
from .provider_scraping import has_error_diagnostics as has_provider_scraping_errors
from .providers import has_error_diagnostics as has_provider_validation_errors
from .providers import validate_provider_sandbox


def provider_factory():
    """Return the BC-NPPD FreshForge provider."""
    return BcNppDatabaseProvider()


class BcNppDatabaseProvider:
    """Executable FreshForge provider for BC-NPPD domain workflow nodes."""

    def metadata(self):
        from freshforge.providers import NodeTypeMetadata, ProviderMetadata

        return ProviderMetadata(
            id="bc_npp_database",
            version="0.1.0a1",
            name="BC-NPPD provider",
            description="Provider source-sweep and review package nodes for BC-NPPD.",
            node_types=(
                NodeTypeMetadata(
                    id="source_sweep",
                    name="Provider source sweep",
                    description="Scrape a provider catalogue into a sandbox.",
                    outputs=("sandbox_dir",),
                    parameters=("provider_id",),
                    artifacts=("sandbox_dir",),
                ),
                NodeTypeMetadata(
                    id="validate_sandbox",
                    name="Validate provider sandbox",
                    description="Validate a provider sandbox directory.",
                    inputs=("sandbox_dir",),
                ),
                NodeTypeMetadata(
                    id="build_review",
                    name="Build provider review",
                    description="Build a static provider review bundle.",
                    inputs=("sandbox_dir",),
                    outputs=("review_dir",),
                    artifacts=("review_dir",),
                ),
                NodeTypeMetadata(
                    id="build_approval_review",
                    name="Build provider approval review",
                    description="Build a static expert approval-review app.",
                    inputs=("sandbox_dir", "poc_dir"),
                    outputs=("approval_review_dir",),
                    parameters=("reviewer",),
                    artifacts=("approval_review_dir",),
                ),
            ),
        )

    def validate_node(self, node, node_type, *, location: str) -> Sequence[Any]:
        from freshforge.records import Diagnostic, DiagnosticSeverity

        diagnostics: list[Diagnostic] = []
        diagnostics.extend(
            _missing_keys(
                required=node_type.inputs,
                actual=node.inputs,
                field_name="inputs",
                location=location,
            )
        )
        diagnostics.extend(
            _missing_keys(
                required=node_type.outputs,
                actual=node.outputs,
                field_name="outputs",
                location=location,
            )
        )
        diagnostics.extend(
            _missing_keys(
                required=node_type.parameters,
                actual=node.parameters,
                field_name="parameters",
                location=location,
            )
        )
        artifacts = node.artifacts if isinstance(node.artifacts, dict) else {}
        diagnostics.extend(
            _missing_keys(
                required=node_type.artifacts,
                actual=artifacts,
                field_name="artifacts",
                location=location,
            )
        )
        if node_type.id == "source_sweep":
            max_pages = node.parameters.get("max_pages", 5)
            if not isinstance(max_pages, int) or max_pages < 1:
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        code="bc_npp_database.max_pages.invalid",
                        message="source_sweep max_pages must be a positive integer.",
                        location=f"{location}.parameters.max_pages",
                    )
                )
        return diagnostics

    def run_node(self, node, node_type, *, context):
        from freshforge.records import ProviderRunResult, RunStatus

        if node_type.id == "source_sweep":
            result = scrape_provider_sandbox(
                str(node.parameters["provider_id"]),
                str(node.parameters.get("database_instance", "vancouver")),
                context.resolve_path(str(node.artifacts["sandbox_dir"])),
                input_dir=_optional_resolved_path(node.parameters.get("input_dir"), context),
                live_fetch=bool(node.parameters.get("live_fetch", False)),
                source_sweep=bool(node.parameters.get("source_sweep", True)),
                max_pages=int(node.parameters.get("max_pages", 5)),
                catalog_url=_optional_string(node.parameters.get("catalog_url")),
                raw_dir=context.resolve_path(
                    str(node.parameters.get("raw_dir", "local/provider_raw"))
                ),
            )
            return ProviderRunResult(
                status=_run_status(not has_provider_scraping_errors(result.diagnostics)),
                outputs={"sandbox_dir": result.path, "counts": result.counts},
                artifacts=result.paths,
                diagnostics=_freshforge_diagnostics(result.diagnostics),
                data=result.to_summary_dict(),
            )

        if node_type.id == "validate_sandbox":
            result = validate_provider_sandbox(
                context.resolve_path(str(node.inputs["sandbox_dir"]))
            )
            return ProviderRunResult(
                status=_run_status(not has_provider_validation_errors(result.diagnostics)),
                outputs={"counts": result.counts},
                diagnostics=_freshforge_diagnostics(result.diagnostics),
                data=result.to_summary_dict(),
            )

        if node_type.id == "build_review":
            result = build_provider_review(
                context.resolve_path(str(node.inputs["sandbox_dir"])),
                context.resolve_path(str(node.artifacts["review_dir"])),
            )
            return ProviderRunResult(
                status=_run_status(not has_provider_scraping_errors(result.diagnostics)),
                outputs={"review_dir": result.path, "counts": result.counts},
                artifacts=result.paths,
                diagnostics=_freshforge_diagnostics(result.diagnostics),
                data=result.to_summary_dict(),
            )

        if node_type.id == "build_approval_review":
            result = build_provider_approval_review(
                context.resolve_path(str(node.inputs["sandbox_dir"])),
                context.resolve_path(str(node.inputs["poc_dir"])),
                context.resolve_path(str(node.artifacts["approval_review_dir"])),
                reviewer=str(node.parameters.get("reviewer", "")),
            )
            return ProviderRunResult(
                status=_run_status(not _has_errors(result.diagnostics)),
                outputs={"approval_review_dir": result.path, "counts": result.counts},
                artifacts=result.paths,
                diagnostics=_freshforge_diagnostics(result.diagnostics),
                data=result.to_summary_dict(),
            )

        return ProviderRunResult(
            status=RunStatus.FAILED,
            diagnostics=(
                _freshforge_diagnostic(
                    "bc_npp_database.node_type.unsupported",
                    f"Unsupported BC-NPPD node type: {node_type.id}",
                    severity="error",
                ),
            ),
        )


def _missing_keys(
    *,
    required: Sequence[str],
    actual: dict[str, Any],
    field_name: str,
    location: str,
) -> list[Any]:
    from freshforge.records import Diagnostic, DiagnosticSeverity

    diagnostics: list[Diagnostic] = []
    for key in required:
        if key not in actual:
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    code=f"bc_npp_database.{field_name}.missing",
                    message=f"Node is missing required {field_name} key '{key}'.",
                    location=f"{location}.{field_name}.{key}",
                )
            )
    return diagnostics


def _freshforge_diagnostics(diagnostics: Sequence[Any]) -> tuple[Any, ...]:
    return tuple(
        _freshforge_diagnostic(
            diagnostic.code,
            diagnostic.message,
            severity=diagnostic.severity.value,
        )
        for diagnostic in diagnostics
    )


def _freshforge_diagnostic(code: str, message: str, *, severity: str):
    from freshforge.records import Diagnostic, DiagnosticSeverity

    severity_value = DiagnosticSeverity.ERROR
    if severity == "warning":
        severity_value = DiagnosticSeverity.WARNING
    elif severity == "info":
        severity_value = DiagnosticSeverity.INFO
    return Diagnostic(severity=severity_value, code=code, message=message)


def _run_status(success: bool):
    from freshforge.records import RunStatus

    return RunStatus.SUCCESS if success else RunStatus.FAILED


def _optional_resolved_path(value: Any, context) -> Any:
    if value in (None, ""):
        return None
    return context.resolve_path(str(value))


def _optional_string(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _has_errors(diagnostics: Sequence[Any]) -> bool:
    return any(diagnostic.severity.value == "error" for diagnostic in diagnostics)
