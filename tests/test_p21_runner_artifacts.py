from pathlib import Path


def test_p21_freshforge_template_documents_downloaded_manifest_flow():
    text = Path("examples/p21_downloaded_provider_approval_freshforge.yaml").read_text(
        encoding="utf-8"
    )

    assert "p21_downloaded_provider_approval" in text
    assert "${USERPROFILE}/Downloads/approval_manifest.csv" in text
    assert "outputs/provider_approval_review/PROV-SATIN/approval_manifest.csv" in text
    assert "provider.copy_downloaded_manifest" in text
    assert "provider.validate_approval_manifest" in text
    assert "provider.apply_approval_preview" in text
    assert "validate-provider-approvals" in text
    assert "apply-provider-approvals" in text
    assert "validate-vancouver-usability" in text
    assert "validate-vancouver-pollinator-module" in text
    assert "provider.write_run_summary" in text


def test_p21_powershell_runner_has_liz_friendly_defaults_and_guards():
    text = Path("scripts/apply-downloaded-provider-approval.ps1").read_text(encoding="utf-8")

    assert 'Join-Path $HOME "Downloads\\approval_manifest.csv"' in text
    assert '$ProviderId = "PROV-SATIN"' in text
    assert '$PreviewDir = "outputs/provider_approved_vancouver"' in text
    assert "Approval manifest not found" in text
    assert "validate-provider-approvals" in text
    assert "apply-provider-approvals" in text
    assert "validate-vancouver-poc-list" in text
    assert "validate-vancouver-evidence" in text
    assert "validate-vancouver-usability" in text
    assert "validate-vancouver-pollinator-module" in text
    assert "usability/index.html" in text
    assert "Tracked product data was not modified." in text


def test_p21_cmd_runner_bypasses_powershell_execution_policy():
    text = Path("scripts/apply-downloaded-provider-approval.cmd").read_text(encoding="utf-8")

    assert "apply-downloaded-provider-approval.ps1" in text
    assert "-ExecutionPolicy Bypass" in text
    assert "%*" in text
    assert "exit /b %ERRORLEVEL%" in text


def test_provider_review_docs_include_simple_runner_and_manual_fallback():
    text = Path("docs/provider-review-workflow.rst").read_text(encoding="utf-8")

    assert "Simple Apply Preview" in text
    assert ".\\scripts\\apply-downloaded-provider-approval.cmd -OpenPreview" in text
    assert (
        "powershell -NoProfile -ExecutionPolicy Bypass -File "
        ".\\scripts\\apply-downloaded-provider-approval.ps1 -OpenPreview"
    ) in text
    assert "examples/p21_downloaded_provider_approval_freshforge.yaml" in text
    assert "bc-nppd validate-provider-approvals path/to/approval_manifest.csv --json" in text
    assert "bc-nppd apply-provider-approvals path/to/approval_manifest.csv" in text
