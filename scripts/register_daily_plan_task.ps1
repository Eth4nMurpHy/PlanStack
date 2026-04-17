$ErrorActionPreference = 'Stop'

param(
    [string]$TaskName = 'PlanStack Daily Prompt',
    [string]$Time = '21:30'
)

$scriptPath = Join-Path $PSScriptRoot 'capture_tomorrow_plan.ps1'
$startTime = [datetime]::ParseExact($Time, 'HH:mm', $null)

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Daily -At $startTime
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
Write-Host "已注册计划任务 '$TaskName'，每天 $Time 提醒你发布第二天计划到 next 页面。"