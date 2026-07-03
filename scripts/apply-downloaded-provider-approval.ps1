param(
    [string]$ManifestPath = (Join-Path $HOME "Downloads\approval_manifest.csv"),
    [string[]]$ManifestPaths = @(),
    [string]$ProviderId = "",
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

function Get-ManifestProviderId {
    param([string]$Path)
    $rows = Import-Csv -LiteralPath $Path
    $providerIds = @($rows | ForEach-Object { $_.provider_id } | Where-Object { $_ } | Sort-Object -Unique)
    if ($providerIds.Count -eq 0) {
        throw "Could not infer provider_id from '$Path'."
    }
    if ($providerIds.Count -gt 1) {
        throw "Manifest '$Path' contains multiple provider_id values: $($providerIds -join ', '). Split it or pass one provider manifest at a time."
    }
    return $providerIds[0]
}

Push-Location $RepoRoot
try {
    if ($ManifestPaths.Count -eq 0) {
        $ManifestPaths = @($ManifestPath)
    }
    elseif ($ManifestPaths.Count -eq 1 -and $ManifestPaths[0].Contains(",")) {
        $ManifestPaths = @($ManifestPaths[0].Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    }

    $ScratchManifests = @()
    foreach ($InputManifest in $ManifestPaths) {
        if (-not (Test-Path -LiteralPath $InputManifest)) {
            throw "Approval manifest not found at '$InputManifest'. Download approval_manifest.csv from the review app, or pass -ManifestPath/-ManifestPaths."
        }
        $InferredProviderId = Get-ManifestProviderId -Path $InputManifest
        if ($ProviderId -and $ProviderId -ne $InferredProviderId) {
            throw "Manifest '$InputManifest' contains provider_id '$InferredProviderId', but -ProviderId was '$ProviderId'."
        }
        $ScratchDir = Join-Path "outputs/provider_approval_review" $InferredProviderId
        $ScratchManifest = Join-Path $ScratchDir "approval_manifest.csv"
        New-Item -ItemType Directory -Force -Path $ScratchDir | Out-Null
        $inputResolved = (Resolve-Path -LiteralPath $InputManifest).Path
        $scratchResolved = $null
        if (Test-Path -LiteralPath $ScratchManifest) {
            $scratchResolved = (Resolve-Path -LiteralPath $ScratchManifest).Path
        }
        if ($inputResolved -ne $scratchResolved) {
            Copy-Item -LiteralPath $InputManifest -Destination $ScratchManifest -Force
        }
        $ScratchManifests += $ScratchManifest
    }

    Write-Host "BC-NPPD provider approval preview" -ForegroundColor Green
    Write-Host "Manifest count: $($ScratchManifests.Count)"
    foreach ($ScratchManifest in $ScratchManifests) {
        Write-Host "Scratch manifest: $ScratchManifest"
    }
    Write-Host "Preview output: $PreviewDir"

    foreach ($ScratchManifest in $ScratchManifests) {
        Invoke-BcNppdStep "Validate approval manifest $ScratchManifest" @(
            "validate-provider-approvals",
            $ScratchManifest,
            "--json"
        )
    }

    $ApplyArgs = @(
        "apply-provider-approval-sequence"
    )
    $ApplyArgs += $ScratchManifests
    $ApplyArgs += @(
        "--poc-dir",
        $PocDir,
        "--out-dir",
        $PreviewDir,
        "--json"
    )
    if ($SkipRegeneration) {
        $ApplyArgs += "--skip-regeneration"
    }
    Invoke-BcNppdStep "Apply approvals cumulatively into ignored preview product" $ApplyArgs

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
        "Manifests: $($ScratchManifests -join ', ')",
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
