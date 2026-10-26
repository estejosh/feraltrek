"""Build the public site (docs/) and RSS feed from data/summaries/. Free tier: headlines only."""
import html, datetime as dt
from email.utils import format_datetime
from common import ROOT, CFG, load

E = html.escape
sums = [s for s in (load(f, {}) for f in (ROOT / "data" / "summaries").glob("*.json")) if not s.get("skip")]
props = {f.stem: load(f, {}) for f in (ROOT / "data" / "proposals").glob("*.json")}
for s in sums:
    s["_created"] = props.get(s["id"], {}).get("created", 0)
sums.sort(key=lambda s: s["_created"], reverse=True)
recent = sums[:60]
site, price, days = CFG["site_url"], CFG["price_usdc"], CFG["days_per_price"]
addr, inbox = CFG["pay_address"], CFG["inbox"]


def day(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%d")


items = "\n".join(
    f"""<article><div class="meta">{E(s['space'])} &middot; {day(s['_created'])}</div>
<h2><a href="{E(s['url'])}">{E(s['title'])}</a></h2><p>{E(s['headline'])}</p>
<div class="meta">{E(s.get('vote', ''))}</div></article>""" for s in recent)

sample = (f"""<div class="box"><b>Sample of the paid analysis</b> ({E(recent[0]['title'])})<br>{E(recent[0]['summary'])}<br>
<span class="meta">Flags: {E(", ".join(recent[0].get("risk_flags", [])))}</span></div>""" if recent else "")
page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Governance Digest: plain-English DAO proposals</title>
<meta name="description" content="New DAO governance proposals and forum discussions from Aave, Uniswap, Arbitrum, ENS, Lido and more, summarized in plain English.">
<link rel="alternate" type="application/rss+xml" title="Governance Digest" href="rss.xml">
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--mute:#6b6b66;--line:#e4e2dc;--acc:#2f5d50}}
@media (prefers-color-scheme:dark){{:root{{--bg:#151514;--fg:#ecebe6;--mute:#9a9992;--line:#2c2c29;--acc:#7fb8a6}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 Georgia,serif}}
main{{max-width:720px;margin:0 auto;padding:24px 16px}}
h1{{font-size:28px;margin:0 0 4px}} h2{{font-size:19px;margin:4px 0}}
a{{color:var(--acc)}} .meta{{color:var(--mute);font:13px/1.4 system-ui,sans-serif}}
article{{border-top:1px solid var(--line);padding:16px 0}}
.box{{border:1px solid var(--line);padding:14px 16px;margin:20px 0;font:15px/1.5 system-ui,sans-serif}}
code{{word-break:break-all}}
</style></head><body><main>
<h1>Governance Digest</h1>
<div class="meta">What DAOs are proposing and discussing, in plain English. Updated daily. Facts only, not advice.
&middot; <a href="rss.xml">RSS</a></div>
<div class="box"><b>Full analysis by email, weekly.</b> Each item with what changes, money involved, who benefits,
open questions and risk flags. {price} USDC on Base = {days} days.<br>
1. Send {price} USDC on <b>Base</b> to <code>{addr}</code><br>
2. Email the transaction hash to <a href="mailto:{inbox}">{inbox}</a> from the address you want the digest sent to.<br>
Access starts at the next daily check.</div>
{sample}
{items or '<p>First items coming soon.</p>'}
<p class="meta">Sources: Snapshot and public DAO forums. Built and run by an autonomous AI project. Not affiliated with any DAO.
All code, revenue and subscriber counts are public: <a href="https://github.com/estejosh/feraltrek">source</a> &middot; <a href="https://github.com/estejosh/feraltrek/blob/main/metrics.json">metrics</a>
&middot; updated {dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</p>
</main></body></html>"""

now = dt.datetime.now(dt.timezone.utc)
rss_items = "\n".join(
    f"""<item><title>{E(s['title'])} ({E(s['space'])})</title><link>{E(s['url'])}</link>
<guid isPermaLink="false">{E(s['id'])}</guid><pubDate>{format_datetime(dt.datetime.fromtimestamp(s['_created'] or now.timestamp(), dt.timezone.utc))}</pubDate>
<description>{E(s['headline'])}</description></item>""" for s in recent)
rss = f"""<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>
<title>Governance Digest</title><link>{site}</link>
<description>New DAO governance proposals and discussions, summarized in plain English.</description>
<lastBuildDate>{format_datetime(now)}</lastBuildDate>
{rss_items}
</channel></rss>"""

docs = ROOT / "docs"
docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(page, encoding="utf-8")
(docs / "rss.xml").write_text(rss, encoding="utf-8")
(docs / ".nojekyll").write_text("", encoding="utf-8")
print(f"site built: {len(recent)} items")

