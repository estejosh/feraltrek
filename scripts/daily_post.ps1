# Daily worker, step 2: rebuild site, check payments, send digest (on digest day), metrics, log, push.
param([string]$Note = "daily run")
$ErrorActionPreference = 'Continue'
Set-Location (Split-Path $PSScriptRoot -Parent)
$out = @()
$out += python scripts\build_site.py 2>&1
$out += python scripts\check_payments.py 2>&1
$out += python scripts\send_digest.py 2>&1
$out += python scripts\metrics.py 2>&1
$out | ForEach-Object { "$_" }
$month = (Get-Date).ToString('yyyy-MM'); New-Item -ItemType Directory -Force log | Out-Null
Add-Content "log\$month.md" ("- {0}: {1} | {2}" -f (Get-Date).ToString('yyyy-MM-dd HH:mm'), $Note, (($out | Select-Object -Last 4) -join ' / '))
& "$PSScriptRoot\push.ps1" "daily: $Note"
