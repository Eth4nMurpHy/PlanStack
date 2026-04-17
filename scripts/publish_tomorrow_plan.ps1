param(
    [string]$PlanDate = (Get-Date).AddDays(1).ToString('yyyy-MM-dd')
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonScript = Join-Path $PSScriptRoot 'planstack.py'
$draftPath = Join-Path (Join-Path $repoRoot '.planstack-drafts') "$PlanDate.md"

if (-not (Test-Path $draftPath)) {
    throw "Draft not found: $draftPath"
}

python $pythonScript publish-next --next-plan $draftPath
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to publish tomorrow draft.'
}

Write-Host "Published tomorrow draft from $draftPath to docs/next.md."