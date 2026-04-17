param(
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$pythonScript = Join-Path $PSScriptRoot 'planstack.py'
$docsDir = Join-Path (Split-Path -Parent $PSScriptRoot) 'docs'
$homePage = Join-Path $docsDir 'index.md'
$nextPage = Join-Path $docsDir 'next.md'

function Get-PlanDate {
    param(
        [string]$Path
    )

    $content = Get-Content -Path $Path -Raw -Encoding UTF8
    $match = [regex]::Match($content, '^# .*Date:\s*(\d{4}-\d{2}-\d{2})\s*$', [System.Text.RegularExpressions.RegexOptions]::Multiline)
    if (-not $match.Success) {
        return $null
    }

    return [datetime]::ParseExact($match.Groups[1].Value, 'yyyy-MM-dd', $null)
}

Write-Host 'Syncing dates first: home -> today, next -> tomorrow.'
python $pythonScript sync-dates
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to sync home and next page dates before rollover.'
}

$homeDate = Get-PlanDate -Path $homePage
$nextDate = Get-PlanDate -Path $nextPage

if ($null -eq $homeDate) {
    throw 'Could not read the date header from docs/index.md.'
}

if ($null -eq $nextDate) {
    Write-Host 'The next page is not a published plan yet. Run capture_tomorrow_plan.ps1 first.'
    exit 1
}

if ($nextDate -le $homeDate) {
    Write-Host "Current home date: $($homeDate.ToString('yyyy-MM-dd'))"
    Write-Host "Current next date: $($nextDate.ToString('yyyy-MM-dd'))"
    Write-Host 'The next page is not ready as tomorrow plan. Run capture_tomorrow_plan.ps1 first.'
    exit 1
}

Write-Host "About to archive $($homeDate.ToString('yyyy-MM-dd')) and switch home to $($nextDate.ToString('yyyy-MM-dd'))."
$confirmation = Read-Host 'Continue? Enter y to proceed'
if ($confirmation -notin @('y', 'Y')) {
    Write-Host 'Canceled. No files were changed.'
    exit 0
}

$arguments = @($pythonScript, 'rollover')
if ($Force) {
    $arguments += '--force'
}

python @arguments
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to archive current plan and activate the published next plan.'
}

Write-Host 'Archive completed. Home page now uses the published next plan.'