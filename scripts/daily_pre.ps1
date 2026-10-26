# Daily worker, step 1: fetch new items and list what needs a summary.
$ErrorActionPreference = 'Continue'
Set-Location (Split-Path $PSScriptRoot -Parent)
git pull -q --ff-only 2>&1 | Out-Null
python scripts\fetch_proposals.py
python scripts\pending.py
