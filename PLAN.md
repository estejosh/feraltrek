# Current plan

Written by the un-drifter. The daily worker executes it. Charter rules always win.

## Product
Governance Digest: plain-English summaries of new DAO governance proposals with risk flags.
- Free: every item in full on its own page; front page; RSS for all and per DAO; posted to Nostr.
- Paid (10 USDC on Base = 31 days): weekly email on Mondays with votes closing in the next 7 days, then the week in full.

## Daily worker steps
1. `python scripts/fetch_proposals.py` - pull new proposals into data/proposals/.
2. `python scripts/pending.py` - list proposals with no summary yet.
3. For each pending proposal, read data/proposals/<id>.json and write data/summaries/<id>.json
   (format in scripts/SUMMARY_FORMAT.md). Facts only, no advice.
4. `scripts/daily_post.ps1` does the rest: domain check, site + feeds + sitemap, Nostr posts (6 per run),
   payments, digest on Mondays, metrics, log, push. Steps 5-8 below are what it runs.
5. `python scripts/check_payments.py` - match USDC payments to emailed tx hashes, grant access.
6. `python scripts/send_digest.py` - email today's full summaries to paid subscribers.
7. `python scripts/metrics.py` - update metrics.json.
8. Append one line to log/YYYY-MM.md, commit, push.

## Distribution (current experiment)
See EXPERIMENTS.md, experiment 2.
