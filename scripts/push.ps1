# Commit everything tracked/new and push with the repo PAT from .env. Never prints the token.
param([string]$Message = "update")
$ErrorActionPreference = 'Continue'
Set-Location (Split-Path $PSScriptRoot -Parent)
git add -A
if (-not (git diff --cached --name-only)) { "nothing to commit"; exit 0 }
# refuse to commit if any real secret value from .env appears in what is staged
$vals = Get-Content .env | Where-Object { $_ -match '^[A-Za-z_]+=.{12,}' } | ForEach-Object { ($_ -split '=', 2)[1].Trim().Trim('"') }
$diff = (git diff --cached) -join "`n"
foreach ($v in $vals) { if ($diff.Contains($v)) { "ABORT push: a value from .env is staged"; git reset -q; exit 1 } }
git commit -q -m $Message
$line = Get-Content .env | Where-Object { $_ -match '^HAIKUFULL_PAT=' } | Select-Object -First 1
$tok = ($line -split '=', 2)[1].Trim().Trim('"')
$b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("x-access-token:$tok"))
git -c "http.extraheader=AUTHORIZATION: basic $b64" push -q origin main 2>&1 | Select-String -NotMatch 'extraheader|vulnerabilit|dependabot|^remote:\s*$'
git log --oneline -1
