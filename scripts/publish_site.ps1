param(
    [string]$Message = ''
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    $status = git status --short
    if (-not $status) {
        Write-Host 'No local changes to publish.'
        exit 0
    }

    if ([string]::IsNullOrWhiteSpace($Message)) {
        $Message = 'Update PlanStack content'
    }

    git add .
    if ($LASTEXITCODE -ne 0) {
        throw 'git add failed.'
    }

    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
        throw 'git commit failed.'
    }

    git push
    if ($LASTEXITCODE -ne 0) {
        throw 'git push failed.'
    }

    Write-Host 'Published to origin/main. GitHub Actions will deploy the site automatically.'
}
finally {
    Pop-Location
}