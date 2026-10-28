# Switch the site to its own domain once DNS points there. Safe to run daily: does nothing until
# digest.fu.observer has a CNAME to estejosh.github.io, and nothing again once switched.
$ErrorActionPreference = 'SilentlyContinue'
Set-Location (Split-Path $PSScriptRoot -Parent)
$domain = 'digest.fu.observer'
$cfgPath = 'config\project.json'
$cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json
if ($cfg.site_url -eq "https://$domain/") { "domain: already on $domain"; exit 0 }
$cname = (Resolve-DnsName $domain -Type CNAME -DnsOnly).NameHost
if ($cname -notmatch 'estejosh\.github\.io') { "domain: waiting for DNS ($domain -> estejosh.github.io)"; exit 0 }
$line = Get-Content .env | Where-Object { $_ -match '^HAIKUFULL_PAT=' } | Select-Object -First 1
$tok = ($line -split '=', 2)[1].Trim().Trim('"')
$h = @{ Authorization = "Bearer $tok"; Accept = 'application/vnd.github+json'; 'X-GitHub-Api-Version' = '2022-11-28' }
try { Invoke-RestMethod -Method Put -Uri https://api.github.com/repos/estejosh/feraltrek/pages -Headers $h -ContentType 'application/json' -Body ('{"cname":"' + $domain + '"}') | Out-Null }
catch { "domain: Pages API refused: $($_.Exception.Response.StatusCode.value__)"; exit 0 }
[IO.File]::WriteAllText("$PWD\docs\CNAME", $domain)
$cfg.site_url = "https://$domain/"
[IO.File]::WriteAllText("$PWD\$cfgPath", ($cfg | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding $false))
python scripts\build_site.py
python scripts\nostr_post.py --profile
"domain: switched to $domain"
