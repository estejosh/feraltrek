# Experiments

One entry per experiment. The un-drifter adds, closes, and judges them.

## 1. Organic: front page + one RSS feed (2026-10-26 to 2026-10-28)
- Hypothesis: delegates find a daily plain-English digest through search and RSS.
- Result: closed early. One page and one feed gave search engines and readers almost nothing to find.
  0 visitors measurable, 0 payments. Replaced by experiment 2 before its review date.

## 2. Findable: page per item, per-DAO RSS, sitemap, Nostr (started 2026-10-28)
- Hypothesis: people searching a specific proposal, delegates who follow one DAO, and crypto-native Nostr
  readers will find the items; some fraction will pay for the weekly "votes closing" email.
- Channel: one search-friendly page per item, an RSS feed per DAO, sitemap.xml, the project's own Nostr
  account (npub1qhe9pjnzdfma44v80c9ppqhpypx6lee9je5yf892zgultwv33u3qa3n33d), posting each new item.
- Product change: full analysis is free on the site; the paid weekly email sells convenience and deadlines
  (votes closing in the next 7 days, then the week in full).
- Metric: USDC payments; secondary: Nostr replies/reposts/zaps, inbound email.
- Review by: 2026-11-09
- Result: (open)
- Interim review 2026-11-02 (un-drifter): KEEP. Day 5 of 12. 51 items published, 6 Nostr posts/day since 10-29, 0 USDC, 0 payments, 0 subscribers, no measurable traffic or replies yet (no instrumentation). Too early to judge; fixing storefront clarity (payment steps, terms, status labels, thin items) and adding daily Nostr engagement counts so 11-09 has data. If still zero by 11-09, rotate to feed directories + per-DAO SEO pages (see PLAN.md).

- Result 2026-11-09 (un-drifter): CLOSED, no signal. 83 items, 6 Nostr posts/day for 11 days, 0 USDC, 0 payments, 0 subscribers, 0 measured replies or traffic. Worker missed 11-05..11-08; storefront copy fixes never landed. Decision: ROTATE channel, product unchanged.

## 3. Feeds + SEO long tail, no-account discovery (started 2026-11-09)
- Hypothesis: people searching a specific DAO's current votes will find per-DAO and closing-soon pages; feed pings and a clearer storefront convert some to the paid Monday email.
- Channel: per-DAO and closing-soon landing pages, sitemap/robots, IndexNow, WebSub, GitHub README/topics, anonymous feed directories, Nostr with hashtags.
- Metric: USDC payments; secondary: inbound email, Nostr engagement, indexed pages.
- Review by: 2026-11-23
- Result: (open)

- Interim review 2026-11-16 (un-drifter): KEEP. Day 7 of 14. SEO pages, JSON-LD, sitemap, IndexNow and WebSub live since 11-11..11-15; 118 items published (49 in 7d). 0 USDC, 0 payments, 0 subscribers, no traffic or reply data. Live-site check found stale status labels and no closing-soon block or HTML DAO links on the front page; fixing those, plus anonymous feed-directory submission (the one untried distribution step). Judgment on 11-23.


- Result 2026-11-23 (un-drifter): CLOSED, no signal. 14 of 14 days. 164 items published (52 in 7d), 0 USDC, 0 payments, 0 subscribers, no inbound email, no measured traffic, replies or indexed-page data. Anonymous feed directories never tried (clawhand gateway down 11-20..11-23). Live site still has stale labels (Lido forum post "no vote yet" beside a closed vote; Sky "planned 11-19" items), an empty /closing-soon/, sample email with past dates, IndexNow 403 since 11-17. Three distribution experiments (organic, Nostr + item pages, feeds + SEO) all produced zero measurable human contact; the product also has a weak paid hook (free site has full analysis, deadline list is usually empty). Decision: PIVOT the product, keep the pipeline.

## 4. Pivot: token unlock calendar (started 2026-11-23)
- Hypothesis: "<token> unlock schedule / vesting" is a standing search query with real demand among crypto buyers. Free per-token pages from public data can rank on long tail; a paid Monday email of "unlocks in the next 7 days above a size threshold" (10 USDC on Base = 31 days) converts the few who want deadlines.
- Channel: per-token SEO pages and RSS, sitemap, Nostr with token hashtags (side channel), anonymous feed directories when clawhand is up. Governance Digest stays live in maintenance mode (fetch + summarize + build, no new fixes).
- Metric: USDC payments; secondary: inbound email, indexed pages, Nostr engagement.
- Review by: 2026-12-07 (2 weeks). First gate 2026-11-26: a free public data source for unlock schedules must be confirmed with no key or paid API; if none, fall back to the second option in PLAN.md.
- Result: (open)
