"""Token unlock pages: /unlocks/, /unlocks/this-week/, /unlocks/<token>/, /unlocks/rss.xml.
Facts only: dates, token amounts, USD value (tokens x price at fetch time) and % of max supply.
Called from build_site.py; also runnable alone for testing."""
import json, html, datetime as dt
from email.utils import format_datetime
from common import ROOT, load

E = html.escape


def n(x, d=0):
    try:
        return f"{float(x):,.{d}f}"
    except Exception:
        return ""


def usd(x):
    return ("$" + n(x)) if isinstance(x, (int, float)) and x != "" else "n/a"


def pct(x):
    return (n(x, 3) + "%") if isinstance(x, (int, float)) and x != "" else "n/a"


def load_tokens():
    toks = []
    for f in sorted((ROOT / "data" / "unlocks").glob("*.json")):
        if f.stem == "index":
            continue
        d = load(f, {})
        if d.get("slug") and d.get("events"):
            toks.append(d)
    return toks


def build(shell, site, docs, now):
    toks = load_tokens()
    t0 = now.timestamp()
    day0 = t0 - (t0 % 86400)
    out = docs / "unlocks"
    out.mkdir(parents=True, exist_ok=True)
    today = now.strftime("%Y-%m-%d")
    fetched = max([t.get("fetched", "") for t in toks] or [today])
    nav = '<p class="meta"><a href="{r}">Governance Digest</a> &middot; <a href="{r}unlocks/">Token unlocks</a> &middot; <a href="{r}unlocks/this-week/">This week</a> &middot; <a href="{r}unlocks/rss.xml">RSS</a></p>'
    note = (f'<p class="meta">Data: DefiLlama emissions datasets, fetched {E(fetched)}. USD value is token amount times the price at fetch time, shown only when a price exists. '
            '% is of the token\'s maximum supply, not circulating supply. Dates are in UTC. Schedules can change; check the linked source. Facts only, not advice.</p>')
    expl = '<p>A token unlock is a date when tokens that were locked under a vesting schedule become eligible to move. This page lists scheduled dates and amounts only.</p>'

    def window(days):
        rows = []
        for t in toks:
            for e in t["events"]:
                if e.get("tokens", 0) > 0 and day0 <= e["ts"] <= day0 + (days + 1) * 86400:
                    rows.append((e["ts"], t, e))
        rows.sort(key=lambda r: (r[0], r[1]["name"]))
        return rows

    def table(rows, rel):
        if not rows:
            return "<p>No scheduled unlocks in this window in our data.</p>"
        tr = "".join(f"<tr><td>{E(e['date'])}</td><td><a href=\"{rel}unlocks/{E(t['slug'])}/\">{E(t['name'])}</a></td>"
                     f"<td style=\"text-align:right\">{n(e['tokens'])}</td><td style=\"text-align:right\">{usd(e.get('usd', ''))}</td>"
                     f"<td style=\"text-align:right\">{pct(e.get('pct_of_max', ''))}</td><td>{E(e.get('groups') or '')}</td></tr>" for _, t, e in rows)
        return ('<table style="width:100%;border-collapse:collapse;font:14px/1.4 system-ui,sans-serif" border="0" cellpadding="4">'
                '<tr style="text-align:left"><th>Date (UTC)</th><th>Token</th><th>Tokens</th><th>USD value</th><th>% of max supply</th><th>Recipient group</th></tr>'
                + tr + "</table>")

    def write(path, title, desc, body, rel, canon, ld=""):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(shell(title, desc, body, canon, rel, ld=ld), encoding="utf-8")

    urls = []
    r30, r7 = window(30), window(7)
    u = site + "unlocks/"
    write(out / "index.html", "Token unlocks in the next 30 days", "Scheduled token unlock and vesting events in the next 30 days, by date, with size.",
          nav.format(r="../") + f"<h1>Token unlocks in the next 30 days</h1>{expl}<p class='meta'>{len(r30)} scheduled events across {len({t['slug'] for _, t, _ in r30})} tokens. {len(toks)} tokens tracked.</p>"
          + table(r30, "../") + note, "../", u)
    urls.append(u)
    u = site + "unlocks/this-week/"
    write(out / "this-week" / "index.html", "Token unlocks this week", "Token unlock and vesting events scheduled in the next 7 days.",
          nav.format(r="../../") + f"<h1>Token unlocks in the next 7 days</h1>{expl}" + table(r7, "../../") + note, "../../", u)
    urls.append(u)

    for t in toks:
        evs = [e for e in t["events"] if e.get("tokens", 0) > 0][:60]
        if not evs:
            continue
        nx = next((e for e in evs if e["ts"] >= day0), evs[0])
        rows = "".join(f"<tr><td>{E(e['date'])}</td><td style=\"text-align:right\">{n(e['tokens'])}</td><td style=\"text-align:right\">{usd(e.get('usd', ''))}</td>"
                       f"<td style=\"text-align:right\">{pct(e.get('pct_of_max', ''))}</td><td>{E(e.get('groups') or '')}</td><td>{E(e.get('type') or '')}</td></tr>" for e in evs)
        price = f"Price used: ${n(t['price_usd'], 4)} per token at fetch time." if isinstance(t.get("price_usd"), (int, float)) else "No price available, so USD values are not shown."
        body = (nav.format(r="../../") + f"<h1>{E(t['name'])} token unlock schedule</h1>{expl}"
                f"<div class='box'><b>Next scheduled event: {E(nx['date'])}</b><br>{n(nx['tokens'])} tokens &middot; {usd(nx.get('usd', ''))} &middot; {pct(nx.get('pct_of_max', ''))} of max supply"
                f"{(' &middot; ' + E(nx['groups'])) if nx.get('groups') else ''}</div>"
                '<table style="width:100%;border-collapse:collapse;font:14px/1.4 system-ui,sans-serif" border="0" cellpadding="4">'
                '<tr style="text-align:left"><th>Date (UTC)</th><th>Tokens</th><th>USD value</th><th>% of max supply</th><th>Group</th><th>Type</th></tr>'
                f"{rows}</table><p class='meta'>{E(price)} Source: <a href=\"{E(t['source'])}\">{E(t['source'])}</a> (summary page: <a href=\"{E(t['link'])}\">{E(t['link'])}</a>).</p>" + note)
        u = site + f"unlocks/{t['slug']}/"
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "Dataset",
             "name": f"{t['name']} token unlock schedule", "url": u, "description": f"Scheduled unlock events for {t['name']}: date, token amount, USD value and % of max supply.",
             "isBasedOn": t["source"], "dateModified": t.get("fetched", today)}).replace("</", "<\\/") + "</script>"
        write(out / t["slug"] / "index.html", f"{t['name']} token unlocks: schedule and next event",
              f"{t['name']} next unlock {nx['date']}: {n(nx['tokens'])} tokens. Full schedule table.", body, "../../", u, ld)
        urls.append(u)

    items = "".join(f"<item><title>{E(t['name'])} unlock {E(e['date'])}: {n(e['tokens'])} tokens ({usd(e.get('usd', ''))})</title><link>{site}unlocks/{E(t['slug'])}/</link>"
                    f"<guid isPermaLink=\"false\">{E(t['slug'])}-{e['ts']}</guid><pubDate>{format_datetime(now)}</pubDate>"
                    f"<description>Scheduled {E(e['date'])} UTC: {n(e['tokens'])} tokens, {pct(e.get('pct_of_max', ''))} of max supply.</description></item>" for _, t, e in r30[:100])
    (out / "rss.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Token unlocks, next 30 days</title><link>{site}unlocks/</link>'
                                 f"<description>Scheduled token unlock events, facts only.</description><lastBuildDate>{format_datetime(now)}</lastBuildDate>{items}</channel></rss>", encoding="utf-8")
    print(f"unlock pages built: {len(toks)} tokens, {len(r30)} events in 30d, {len(r7)} in 7d")
    return urls, r7, toks


if __name__ == "__main__":
    import sys
    sys.exit("run via build_site.py")
