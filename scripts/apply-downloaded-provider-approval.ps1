param(
    [string]$ManifestPath = (Join-Path $HOME "Downloads\approval_manifest.csv"),
    [string]$ProviderId = "PROV-SATIN",
    [string]$PocDir = "data/poc/vancouver",
    [string]$PreviewDir = "outputs/provider_approved_vancouver",
    [switch]$SkipRegeneration,
    [switch]$OpenPreview
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$BcNppd = Join-Path $RepoRoot ".venv\Scripts\bc-nppd.exe"
if (-not (Test-Path -LiteralPath $BcNppd)) {
    $BcNppd = "bc-nppd"
}

function Invoke-BcNppdStep {
    param(
        [string]$Label,
        [string[]]$Arguments
    )
    Write-Host ""
    Write-Host "==> $Label" -ForegroundColor Cyan
    & $BcNppd @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Label"
    }
}

Push-Location $RepoRoot
try {
    if (-not (Test-Path -LiteralPath $ManifestPath)) {
        throw "Approval manifest not found at '$ManifestPath'. Download approval_manifest.csv from the review app, or pass -ManifestPath."
    }

    $ScratchDir = Join-Path "outputs/provider_approval_review" $ProviderId
    $ScratchManifest = Join-Path $ScratchDir "approval_manifest.csv"
    New-Item -ItemType Directory -Force -Path $ScratchDir | Out-Null
    Copy-Item -LiteralPath $ManifestPath -Destination $ScratchManifest -Force

    Write-Host "BC-NPPD provider approval preview" -ForegroundColor Green
    Write-Host "Provider: $ProviderId"
    Write-Host "Downloaded manifest: $ManifestPath"
    Write-Host "Scratch manifest: $ScratchManifest"
    Write-Host "Preview output: $PreviewDir"

    Invoke-BcNppdStep "Validate downloaded approval manifest" @(
        "validate-provider-approvals",
        $ScratchManifest,
        "--json"
    )

    $ApplyArgs = @(
        "apply-provider-approvals",
        $ScratchManifest,
        "--poc-dir",
        $PocDir,
        "--out-dir",
        $PreviewDir,
        "--json"
    )
    if ($SkipRegeneration) {
        $ApplyArgs += "--skip-regeneration"
    }
    Invoke-BcNppdStep "Apply approvals into ignored preview product" $ApplyArgs

    Invoke-BcNppdStep "Validate preview provider data" @(
        "validate-provider-approvals",
        (Join-Path $PreviewDir "provider_data"),
        "--json"
    )
    Invoke-BcNppdStep "Validate preview plant list" @(
        "validate-vancouver-poc-list",
        $PreviewDir,
        "--json"
    )

    if (-not $SkipRegeneration) {
        Invoke-BcNppdStep "Validate preview evidence hardening" @(
            "validate-vancouver-evidence",
            (Join-Path $PreviewDir "evidence_hardening"),
            "--json"
        )
        Invoke-BcNppdStep "Validate preview usability app" @(
            "validate-vancouver-usability",
            (Join-Path $PreviewDir "usability"),
            "--json"
        )
        Invoke-BcNppdStep "Validate preview pollinator module" @(
            "validate-vancouver-pollinator-module",
            (Join-Path $PreviewDir "pollinator_module"),
            "--json"
        )
    }

    $PreviewHtml = Join-Path $PreviewDir "usability/index.html"
    $SummaryPath = Join-Path $PreviewDir "provider_approval_preview_summary.txt"
    $summary = @(
        "BC-NPPD provider approval preview complete.",
        "Provider: $ProviderId",
        "Manifest: $ScratchManifest",
        "Preview directory: $PreviewDir",
        "Preview app: $PreviewHtml",
        "Tracked product data was not modified."
    )
    New-Item -ItemType Directory -Force -Path $PreviewDir | Out-Null
    $summary | Set-Content -Path $SummaryPath -Encoding utf8

    Write-Host ""
    Write-Host "Preview ready." -ForegroundColor Green
    Write-Host "Open: $PreviewHtml"
    Write-Host "Summary: $SummaryPath"
    Write-Host "Tracked product data was not modified."

    if ($OpenPreview -and (Test-Path -LiteralPath $PreviewHtml)) {
        Invoke-Item $PreviewHtml
    }
}
finally {
    Pop-Location
}
