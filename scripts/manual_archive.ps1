param(
    [switch]$Force,
    [switch]$BlankTemplate,
    [switch]$Yes
)

$ErrorActionPreference = 'Stop'

$pythonScript = Join-Path $PSScriptRoot 'manual_archive.py'
$docsDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'docs'
$homePage = Join-Path $docsDir 'index.md'

function Get-PlanDate {
    param(
        [string]$Path
    )

    $content = Get-Content -Path $Path -Raw -Encoding UTF8
    $match = [regex]::Match($content, '^# .*Date:\s*(\d{4}-\d{2}-\d{2})\s*$', [System.Text.RegularExpressions.RegexOptions]::Multiline)
    if (-not $match.Success) {
        throw 'Could not read the date header from docs/index.md.'
    }

    return [datetime]::ParseExact($match.Groups[1].Value, 'yyyy-MM-dd', $null)
}

$homeDate = Get-PlanDate -Path $homePage
$nextDate = $homeDate.AddDays(1)

Write-Host "Detected home date: $($homeDate.ToString('yyyy-MM-dd'))"
Write-Host "Manual archive target: docs/History/$($homeDate.ToString('yyyy-MM-dd')).md"
Write-Host "Home page will advance to: $($nextDate.ToString('yyyy-MM-dd'))"

if (-not $Yes) {
    $confirmation = Read-Host 'Continue? Enter y to proceed'
    if ($confirmation -notin @('y', 'Y')) {
        Write-Host 'Canceled. No files were changed.'
        exit 0
    }
}

$arguments = @($pythonScript)
if ($Force) {
    $arguments += '--force'
}
if ($BlankTemplate) {
    $arguments += '--blank-template'
}

python @arguments
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to archive current home page and advance to next day.'
}

Write-Host 'Manual archive completed. Current home page has advanced by one day.'
