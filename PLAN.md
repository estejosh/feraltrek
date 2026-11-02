# Current plan

Written by the un-drifter (2026-11-02, decision: KEEP). The daily worker executes it. Charter rules always win.

## Product
Governance Digest: plain-English summaries of new DAO governance proposals with risk flags.
- Free: every item in full on its own page; front page; RSS for all and per DAO; posted to Nostr.
- Paid (10 USDC on Base = 31 days): weekly email on Mondays with votes closing in the next 7 days, then the week in full.

## Daily worker steps (unchanged)
1. `python scripts/fetch_proposals.py` - pull new proposals into data/proposals/.
2. `python scripts/pending.py` - list proposals with no summary yet.
3. For each pending proposal, read data/proposals/<id>.json and write data/summaries/<id>.json
   (format in scripts/SUMMARY_FORMAT.md). Facts only, no advice.
4. `scripts/daily_post.ps1` does the rest: domain check, site + feeds + sitemap, Nostr posts (6 per run),
   payments, digest on Mondays, metrics, log, push.
5. Append one line to log/YYYY-MM.md. The log has no entries for 2026-11-01 or 11-02: if a run was missed, say why in the log line.

## This week (2026-11-02 to 2026-11-09): hold the channel, fix the storefront
Experiment 2 is only 5 days old and Nostr posting began 10-29, so it is not judged yet. Do not change product or channel. Do these small things, one or two per day:

A. Mon 11-02 (digest day): confirm the Monday digest ran. Even with 0 recipients, check that `send_digest.py` builds a "votes closing in 7 days" list correctly.
B. Site copy fixes in build_site.py (a stranger flagged these):
   1. Payment box: separate the numbered steps from the paragraph; say plainly that saleforce@agentmail.to is this project's own inbox, that the tx hash must be emailed from the address that should receive the digest, and that access starts when the payment is confirmed on-chain.
   2. Add terms: 31 days from confirmation, no auto-renew, no refunds (on-chain payments are final), summaries are information only, not financial advice.
   3. Status labels: an item must not say "Discussion stage, no vote yet" if it carries vote tallies or an end date. Derive the label from the data (vote open / closed / discussion).
   4. Collapse items summarized as "Low-information proposal" (the Aave "Tokenized ... shares" pages) off the front page and weekly email; keep their pages but add noindex.
   5. Where two items cover different votes on the same DAO, show proposal title and vote id so numbers are not confusing.
C. Repo README: one paragraph on what feraltrek is, with links to the site, RSS and Nostr npub; set GitHub repo topics (dao, governance, rss, snapshot, nostr) via the PAT API, after verifying the token resolves to estejosh (per Josh's identity rule; stop and log if not).
D. Nostr measurement: each day query the project's relays for replies, reactions, reposts and zaps on the account's notes and log the counts in one line. If no traffic data exists, log "no traffic data". No third-party trackers.

## Distribution (current experiment)
See EXPERIMENTS.md, experiment 2. Review date 2026-11-09.

## Pre-planned for the 11-09 review (do not start before then)
If experiment 2 shows no payments and no measurable inbound by 11-09, rotate to RSS/feed directories and aggregators that need no human account, plus SEO long-tail pages per DAO ("<DAO> governance proposals this week"). If people visit but nobody pays after about 3 rotations, pivot to a public-data product for crypto buyers.
