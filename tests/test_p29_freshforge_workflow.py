from pathlib import Path

import pytest

WORKFLOW_FILES = [
    Path("examples/workflows/provider_source_review.yaml"),
    Path("examples/workflows/provider_source_review_fixture.yaml"),
    Path("examples/workflows/providers/PROV-SATIN.yaml"),
    Path("examples/workflows/providers/PROV-NWM.yaml"),
    Path("examples/workflows/providers/PROV-WCS.yaml"),
    Path("examples/workflows/providers/PROV-PREMIER.yaml"),
    Path("examples/p19_provider_source_sweep_freshforge.yaml"),
]


def test_p29_provider_workflows_use_freshforge_provider_nodes():
    for path in WORKFLOW_FILES:
        text = path.read_text(encoding="utf-8")
        assert "provider: bc_npp_database.source_sweep" in text
        assert "provider: bc_npp_database.validate_sandbox" in text
        assert "provider: bc_npp_database.build_review" in text
        assert "provider: bc_npp_database.build_approval_review" in text
        assert "command:" not in text
        assert "bc-nppd" not in text


def test_p29_provider_overlay_paths_are_ignored_output_locations():
    for provider_id in ("PROV-SATIN", "PROV-NWM", "PROV-WCS", "PROV-PREMIER"):
        text = Path(f"examples/workflows/providers/{provider_id}.yaml").read_text(
            encoding="utf-8"
        )
        assert f"provider_id: {provider_id}" in text
        assert f"outputs/provider_sandbox_source_sweep/{provider_id}" in text
        assert f"outputs/provider_review_source_sweep/{provider_id}" in text
        assert f"outputs/provider_approval_review/{provider_id}" in text
        assert "raw_dir: local/provider_raw" in text


def test_p29_launcher_invokes_freshforge_not_bc_nppd_steps():
    cmd = Path("scripts/build-provider-source-review.cmd").read_text(encoding="utf-8")
    ps1 = Path("scripts/build-provider-source-review.ps1").read_text(encoding="utf-8")

    assert "build-provider-source-review.ps1" in cmd
    assert "-ExecutionPolicy Bypass" in cmd
    assert "freshforge.exe" in ps1
    assert "freshforge run" in ps1.lower() or "& $FreshForge run" in ps1
    assert "FreshForge is not available" in ps1
    assert "Get-ApprovalReviewPath" in ps1
    assert "bc-nppd scrape-provider-sandbox" not in ps1
    assert "bc-nppd build-provider-review" not in ps1


def test_p29_contracts_reject_parallel_orchestrators():
    agents = Path("AGENTS.md").read_text(encoding="utf-8")
    contributing = Path("CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "FreshForge is the preferred UBC-FRESH workflow runner" in agents
    assert "Do not build a parallel package-specific orchestration framework" in agents
    assert "Use FreshForge YAML for reusable multi-step workflows" in contributing
    assert "package-specific mini-orchestrators" in contributing


def test_p29_freshforge_provider_metadata_when_available():
    pytest.importorskip("freshforge")

    from bc_npp_database.freshforge_provider import provider_factory

    metadata = provider_factory().metadata()
    assert metadata.id == "bc_npp_database"
    node_type_ids = {node_type.id for node_type in metadata.node_types}
    assert {
        "source_sweep",
        "validate_sandbox",
        "build_review",
        "build_approval_review",
    } <= node_type_ids
