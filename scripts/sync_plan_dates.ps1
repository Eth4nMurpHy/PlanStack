param(
    [string]$BaseDate = (Get-Date).ToString('yyyy-MM-dd')
)

$ErrorActionPreference = 'Stop'

$pythonScript = Join-Path $PSScriptRoot 'planstack.py'

python $pythonScript sync-dates --base-date $BaseDate
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to sync home and next page dates.'
}

Write-Host "Dates synced. Home is $BaseDate and next is $((Get-Date $BaseDate).AddDays(1).ToString('yyyy-MM-dd'))."