"""Build the public site (docs/): front page, one page per item, per-DAO RSS feeds, sitemap.
Free: every item in full on the site. Paid: the weekly email with votes closing soon."""
import html, json, re, datetime as dt
from email.utils import format_datetime
from common import ROOT, CFG, load

E = html.escape
DOCS = ROOT / "docs"
SITE = CFG["site_url"].rstrip("/") + "/"
now = dt.datetime.now(dt.timezone.utc)
props = {f.stem: load(f, {}) for f in (ROOT / "data" / "proposals").glob("*.json")}
sums = [s for s in (load(f, {}) for f in (ROOT / "data" / "summaries").glob("*.json")) if not s.get("skip")]
DAO = {"aave.eth": "aave", "uniswapgovernance.eth": "uniswap", "arbitrumfoundation.eth": "arbitrum", "ens.eth": "ens",
       "lido-snapshot.eth": "lido", "gitcoindao.eth": "gitcoin", "balancer.eth": "balancer", "safe.eth": "safe",
       "cow.eth": "cow", "stgdao.eth": "stargate", "opcollective.eth": "optimism", "curve.eth": "curve"}
for s in sums:
    s["space"] = DAO.get(s["space"], s["space"])
    s["_created"] = props.get(s["id"], {}).get("created") or 0
    s["_slug"] = re.sub(r"[^a-z0-9]+", "-", f"{s['space']} {s['title']}".lower()).strip("-")[:80] + "-" + s["id"][-6:]
sums.sort(key=lambda s: s["_created"], reverse=True)


def status(s):
    pr = props.get(s["id"], {})
    if pr.get("source") == "snapshot" or s["id"].startswith("0x"):
        end = pr.get("end")
        if pr.get("state") == "active" and end:
            return "Vote open, ends " + day(end)
        return "Vote closed" + (", ended " + day(end) if end else "")
    return "Discussion, no vote yet"


def ref(s):
    i = s["id"]
    return ("Vote " + i[:6] + "\u2026" + i[-4:]) if i.startswith("0x") else "Forum thread " + i.rsplit("-", 1)[-1]


def lowinfo(s):
    return s.get("headline", "").strip().lower().startswith("low-information")


def day(ts):
    return dt.datetime.fromtimestamp(ts or now.timestamp(), dt.timezone.utc).strftime("%Y-%m-%d")


CSS = """:root{--bg:#fbfaf7;--fg:#1d1d1b;--mute:#6b6b66;--line:#e4e2dc;--acc:#2f5d50}
@media (prefers-color-scheme:dark){:root{--bg:#151514;--fg:#ecebe6;--mute:#9a9992;--line:#2c2c29;--acc:#7fb8a6}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 Georgia,serif}
main{max-width:720px;margin:0 auto;padding:24px 16px}h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:4px 0}
a{color:var(--acc)}.meta{color:var(--mute);font:13px/1.4 system-ui,sans-serif}
article{border-top:1px solid var(--line);padding:16px 0}code{word-break:break-all}
.box{border:1px solid var(--line);padding:14px 16px;margin:20px 0;font:15px/1.5 system-ui,sans-serif}"""


def shell(title, desc, body, canonical, rel="", noindex=False, ld=""):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title>
<meta name="description" content="{E(desc)}"><link rel="canonical" href="{canonical}">{'<meta name="robots" content="noindex">' if noindex else ''}
<link rel="alternate" type="application/rss+xml" title="Governance Digest" href="{rel}rss.xml">
{ld}<style>{CSS}</style></head><body><main>{body}
<p class="meta">Sources: Snapshot and public DAO forums. Built and run by an autonomous AI project. Not affiliated with any DAO.
Facts only, not advice. All code, revenue and subscriber counts are public:
<a href="https://github.com/estejosh/feraltrek">source</a> &middot; <a href="https://github.com/estejosh/feraltrek/blob/main/metrics.json">metrics</a>
&middot; updated {now.strftime("%Y-%m-%d %H:%M UTC")}</p></main></body></html>"""


def paybox():
    return f"""<div class="box"><b>Paid weekly email: deadlines pushed to your inbox</b>
<p>Free: this site, which you have to remember to check. Paid: every Monday an email lists the votes closing in the next 7 days, sorted by deadline, then the week's items in full.</p>
<details><summary>Sample of the weekly email</summary><pre style="white-space:pre-wrap">Closing in the next 7 days
1. [dao] Proposal title - vote ends 2026-11-16 - one-line summary
2. [dao] Proposal title - vote ends 2026-11-18 - one-line summary
The week in full
[dao] Proposal title: full plain-English analysis and flags</pre></details>
<p><b>{CFG['price_usdc']} USDC on Base = {CFG['days_per_price']} days.</b></p>
<ol>
<li>Send {CFG['price_usdc']} USDC on <b>Base</b> to <code>{CFG['pay_address']}</code></li>
<li>Email the transaction hash to <a href="mailto:{CFG['inbox']}">{CFG['inbox']}</a>, which is this project's own inbox. Send it from the address that should receive the digest.</li>
<li>Access starts when the payment is confirmed on-chain.</li>
</ol>
<p class="meta">Terms: {CFG['days_per_price']} days from on-chain confirmation, no auto-renew, no refunds (on-chain payments are final). Information only, not financial advice.</p></div>"""


def card(s, rel):
    if lowinfo(s):
        return f"""<article><div class="meta">{E(s['space'])} &middot; {day(s['_created'])} &middot; {E(ref(s))}</div>
<details><summary>Low-information item: <a href="{rel}p/{s['_slug']}.html">{E(s['title'])}</a></summary></details></article>"""
    return f"""<article><div class="meta">{E(s['space'])} &middot; {day(s['_created'])} &middot; {E(ref(s))}</div>
<h2><a href="{rel}p/{s['_slug']}.html">{E(s['title'])}</a></h2><p>{E(s['headline'])}</p>
<div class="meta">{E(status(s))} &middot; {E(s.get('vote', ''))}</div></article>"""


def rss(items, title, link):
    body = "\n".join(f"""<item><title>{E(s['title'])} ({E(s['space'])})</title><link>{SITE}p/{s['_slug']}.html</link>
<guid isPermaLink="false">{E(s['id'])}</guid><pubDate>{format_datetime(dt.datetime.fromtimestamp(s['_created'] or now.timestamp(), dt.timezone.utc))}</pubDate>
<description>{E(s['headline'])}</description></item>""" for s in items[:50])
    return f"""<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{E(title)}</title><link>{link}</link>
<description>New DAO governance proposals and discussions, summarized in plain English.</description>
<lastBuildDate>{format_datetime(now)}</lastBuildDate>
{body}
</channel></rss>"""


(DOCS / "p").mkdir(parents=True, exist_ok=True)
(DOCS / "feeds").mkdir(exist_ok=True)
spaces = sorted({s["space"] for s in sums})

# item pages (full analysis, free; good for search)
for s in sums:
    flags = ", ".join(s.get("risk_flags", []))
    body = f"""<p class="meta"><a href="../">Governance Digest</a> &middot; <a href="../dao/{E(s['space'])}/">{E(s['space'])} proposals</a> &middot; <a href="../closing-soon/">Closing soon</a> &middot; {day(s['_created'])}</p>
<h1>{E(s['title'])}</h1><p><b>{E(s['headline'])}</b></p><p>{E(s['summary'])}</p>
<p class="meta">Flags: {E(flags)}<br>Status: {E(status(s))}. {E(s.get('vote', ''))}<br>Reference: {E(ref(s))}<br>Source: <a href="{E(s['url'])}">{E(s['url'])}</a></p>
{paybox()}"""
    (DOCS / "p" / f"{s['_slug']}.html").write_text(
        shell(f"{s['title']} ({s['space']}) explained", s["headline"], body, f"{SITE}p/{s['_slug']}.html", "../", noindex=lowinfo(s)), encoding="utf-8")

# front page
feeds = " ".join(f'<a href="feeds/{E(sp)}.xml">{E(sp)}</a>' for sp in spaces)
front = f"""<h1>Governance Digest</h1>
<div class="meta">What DAOs are proposing and discussing, in plain English. Updated daily.
&middot; <a href="rss.xml">RSS (all)</a> &middot; per DAO: {feeds}</div>
{paybox()}
{''.join(card(s, '') for s in sums[:60]) or '<p>First items coming soon.</p>'}"""
(DOCS / "index.html").write_text(shell("Governance Digest: plain-English DAO proposals",
    "New DAO governance proposals and forum discussions from Aave, Uniswap, Arbitrum, ENS, Lido and more, in plain English.",
    front, SITE), encoding="utf-8")

# feeds
(DOCS / "rss.xml").write_text(rss(sums, "Governance Digest", SITE), encoding="utf-8")
for sp in spaces:
    (DOCS / "feeds" / f"{sp}.xml").write_text(rss([s for s in sums if s["space"] == sp], f"Governance Digest: {sp}", SITE), encoding="utf-8")


# SEO pages: per-DAO (last 14 days) and closing-soon (votes ending within 7 days)
def ends(s):
    pr = props.get(s["id"], {})
    return pr.get("end") if pr.get("state") == "active" and pr.get("end") else None


def line(s, rel):
    return f"""<article><div class="meta">{day(s['_created'])} &middot; {E(status(s))}</div>
<h2><a href="{rel}p/{s['_slug']}.html">{E(s['title'])}</a></h2><p>{E(s['headline'])}</p></article>"""


def ldjson(name, url, items, rel):
    import json as _j
    return '<script type="application/ld+json">' + _j.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": name, "url": url,
        "hasPart": [{"@type": "Article", "headline": s["title"], "url": f"{SITE}p/{s['_slug']}.html"} for s in items[:20]]}).replace("</", "<\\/") + "</script>"


cut = now.timestamp() - 14 * 86400
urls_extra = []
for sp in spaces:
    its = [s for s in sums if s["space"] == sp and not lowinfo(s) and s["_created"] >= cut]
    d = DOCS / "dao" / sp
    d.mkdir(parents=True, exist_ok=True)
    name = f"{sp.title()} governance proposals: this week"
    body = f"""<p class="meta"><a href="../../">Governance Digest</a> &middot; <a href="../../closing-soon/">Closing soon</a> &middot; <a href="../../feeds/{E(sp)}.xml">RSS for {E(sp)}</a></p>
<h1>{E(name)}</h1><p class="meta">Items from the last 14 days.</p>{''.join(line(s, '../../') for s in its) or '<p>No new items in the last 14 days.</p>'}"""
    u = f"{SITE}dao/{sp}/"
    (d / "index.html").write_text(shell(name, f"{sp.title()} DAO governance proposals and discussions from the last 14 days, summarized in plain English.", body, u, "../../", noindex=not its, ld=ldjson(name, u, its, "../../")), encoding="utf-8")
    if its:
        urls_extra.append(u)
soon = sorted([s for s in sums if ends(s) and now.timestamp() <= ends(s) <= now.timestamp() + 7 * 86400], key=ends)
(DOCS / "closing-soon").mkdir(exist_ok=True)
body = f"""<p class="meta"><a href="../">Governance Digest</a></p><h1>DAO votes closing in the next 7 days</h1>
{''.join(f"<article><div class='meta'>{E(s['space'])} &middot; vote ends {day(ends(s))}</div><h2><a href='../p/{s['_slug']}.html'>{E(s['title'])}</a></h2><p>{E(s['headline'])}</p></article>" for s in soon) or '<p>No open votes in our data end within 7 days.</p>'}"""
u = SITE + "closing-soon/"
(DOCS / "closing-soon" / "index.html").write_text(shell("DAO votes closing in the next 7 days", "Governance votes that end within a week, sorted by deadline.", body, u, "../", ld=ldjson("Votes closing soon", u, soon, "../")), encoding="utf-8")
urls_extra.append(u)

# sitemap + robots + nostr identity (NIP-05)
urls = [SITE] + urls_extra + [f"{SITE}p/{s['_slug']}.html" for s in sums if not lowinfo(s)]
(DOCS / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>", encoding="utf-8")
(DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n", encoding="utf-8")
(DOCS / ".nojekyll").write_text("", encoding="utf-8")
pub = load(ROOT / "config" / "nostr_public.json", {})
if pub.get("pk_hex"):
    (DOCS / ".well-known").mkdir(exist_ok=True)
    (DOCS / ".well-known" / "nostr.json").write_text(json.dumps({"names": {"digest": pub["pk_hex"]}}), encoding="utf-8")
print(f"site built: {len(sums)} items, {len(spaces)} DAO feeds")
