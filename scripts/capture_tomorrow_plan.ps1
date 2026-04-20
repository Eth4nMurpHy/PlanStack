param(
    [string]$PlanDate = (Get-Date).AddDays(1).ToString('yyyy-MM-dd'),
    [switch]$KeepDraft,
    [switch]$BlankTemplate,
    [switch]$NoEditor,
    [switch]$OpenInNotepad
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonScript = Join-Path $PSScriptRoot 'planstack.py'
$draftDir = Join-Path $repoRoot '.planstack-drafts'
$draftPath = Join-Path $draftDir "$PlanDate.md"

New-Item -ItemType Directory -Path $draftDir -Force | Out-Null

if (-not (Test-Path $draftPath)) {
    if ($BlankTemplate) {
        python $pythonScript new-template --date $PlanDate --output $draftPath
    }
    else {
        python $pythonScript derive-template --date $PlanDate --output $draftPath
    }
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to generate tomorrow plan draft.'
    }
}

Write-Host "Draft path: $draftPath"
if ($BlankTemplate) {
    Write-Host 'Using a blank template for tomorrow.'
}
else {
    Write-Host 'Using today home page as the base for tomorrow, with review cleared and checked tasks reset.'
}
if ($NoEditor) {
    Write-Host 'NoEditor is now the default behavior. Edit this draft in VS Code, then publish it manually.'
}

if (-not $OpenInNotepad) {
    Write-Host 'Edit this draft in VS Code, then publish it manually.'
    Write-Host "Publish command: python .\scripts\planstack.py publish-next --next-plan `"$draftPath`""
    exit 0
}

Write-Host 'Fill it in with Notepad, save, and close it. The script will publish it to next without touching today home page.'

Start-Process notepad.exe -ArgumentList $draftPath -Wait

$confirmation = Read-Host "Publish $PlanDate to the next page? Enter y to continue"
if ($confirmation -notin @('y', 'Y')) {
    Write-Host 'Canceled. No files were changed.'
    exit 0
}

python $pythonScript publish-next --next-plan $draftPath
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to publish tomorrow plan.'
}

if (-not $KeepDraft) {
    Remove-Item $draftPath -Force
}

Write-Host 'Tomorrow plan is now published to the next page. Today home page is unchanged.'