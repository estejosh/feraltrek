# Current plan

Written by the un-drifter. The daily worker executes it. Charter rules always win.

## Product
Governance Digest: plain-English summaries of new DAO governance proposals with risk flags.
- Free: headline per proposal on the site and RSS.
- Paid (10 USDC on Base = 31 days): full analysis by email every day there is something new.

## Daily worker steps
1. `python scripts/fetch_proposals.py` - pull new proposals into data/proposals/.
2. `python scripts/pending.py` - list proposals with no summary yet.
3. For each pending proposal, read data/proposals/<id>.json and write data/summaries/<id>.json
   (format in scripts/SUMMARY_FORMAT.md). Facts only, no advice.
4. `python scripts/build_site.py` - rebuild docs/ (site + RSS).
5. `python scripts/check_payments.py` - match USDC payments to emailed tx hashes, grant access.
6. `python scripts/send_digest.py` - email today's full summaries to paid subscribers.
7. `python scripts/metrics.py` - update metrics.json.
8. Append one line to log/YYYY-MM.md, commit, push.

## Distribution (current experiment)
See EXPERIMENTS.md, experiment 1.
