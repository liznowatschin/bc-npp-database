param(
    [string]$ProviderId = "PROV-SATIN",
    [string]$WorkflowPath = "",
    [string]$Reviewer = "",
    [int]$MaxPages = 0,
    [string]$CatalogUrl = "",
    [switch]$OpenReview
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Resolve-FreshForge {
    $localFreshForge = Join-Path $RepoRoot ".venv\Scripts\freshforge.exe"
    if (Test-Path -LiteralPath $localFreshForge) {
        return $localFreshForge
    }
    $command = Get-Command freshforge -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }
    throw "FreshForge is not available. Install the workflow extra first: python -m pip install -e .[workflow]"
}

function Update-WorkflowText {
    param([string]$Text)
    if ($Reviewer) {
        $Text = $Text -replace '(?m)^(\s*reviewer:\s*).+$', "`${1}$Reviewer"
    }
    if ($MaxPages -gt 0) {
        $Text = $Text -replace '(?m)^(\s*max_pages:\s*)\d+(\s*)$', "`${1}$MaxPages`${2}"
    }
    if ($CatalogUrl) {
        $Text = $Text -replace '(?m)^(\s*catalog_url:\s*).+$', "`${1}$CatalogUrl"
    }
    return $Text
}

function Get-ApprovalReviewPath {
    param([string]$Path)
    $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match '^\s*approval_review_dir:\s*(.+?)\s*$' } | Select-Object -First 1
    if ($line -and $line -match '^\s*approval_review_dir:\s*(.+?)\s*$') {
        return $Matches[1]
    }
    return (Join-Path "outputs\provider_approval_review" $ProviderId)
}

Push-Location $RepoRoot
try {
    if (-not $WorkflowPath) {
        $WorkflowPath = Join-Path "examples\workflows\providers" "$ProviderId.yaml"
    }
    if (-not (Test-Path -LiteralPath $WorkflowPath)) {
        throw "FreshForge workflow not found at '$WorkflowPath'. Check ProviderId or pass -WorkflowPath."
    }

    $RunWorkflow = $WorkflowPath
    if ($Reviewer -or $MaxPages -gt 0 -or $CatalogUrl) {
        $runDir = Join-Path "outputs\provider_workflow_runs" $ProviderId
        New-Item -ItemType Directory -Force -Path $runDir | Out-Null
        $RunWorkflow = Join-Path $runDir "provider_source_review.yaml"
        $text = Get-Content -LiteralPath $WorkflowPath -Raw
        Set-Content -LiteralPath $RunWorkflow -Value (Update-WorkflowText -Text $text) -Encoding UTF8
    }

    $FreshForge = Resolve-FreshForge
    Write-Host "BC-NPPD provider source-review workflow" -ForegroundColor Green
    Write-Host "Provider: $ProviderId"
    Write-Host "Workflow: $RunWorkflow"
    Write-Host ""
    Write-Host "==> Run FreshForge workflow" -ForegroundColor Cyan
    & $FreshForge run $RunWorkflow --workdir $RepoRoot --json
    if ($LASTEXITCODE -ne 0) {
        throw "FreshForge workflow failed."
    }

    $ReviewPath = Get-ApprovalReviewPath -Path $RunWorkflow
    $ReviewIndex = Join-Path $ReviewPath "index.html"
    Write-Host ""
    Write-Host "Provider review package complete." -ForegroundColor Green
    Write-Host "Approval review app: $ReviewIndex"
    Write-Host "Generated outputs remain ignored until explicitly promoted."
    if ($OpenReview) {
        if (Test-Path -LiteralPath $ReviewIndex) {
            Invoke-Item $ReviewIndex
        }
        else {
            Write-Warning "Review app was not found at '$ReviewIndex'."
        }
    }
}
finally {
    Pop-Location
}
