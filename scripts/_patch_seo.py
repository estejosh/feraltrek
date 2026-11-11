import pathlib
p = pathlib.Path(__file__).with_name("build_site.py")
t = p.read_text(encoding="utf-8")
if "closing-soon" in t:
    raise SystemExit("already patched")

# internal links on every item page
t = t.replace("""<p class="meta"><a href="../">Governance Digest</a> &middot; {E(s['space'])} &middot; {day(s['_created'])}</p>""",
"""<p class="meta"><a href="../">Governance Digest</a> &middot; <a href="../dao/{E(s['space'])}/">{E(s['space'])} proposals</a> &middot; <a href="../closing-soon/">Closing soon</a> &middot; {day(s['_created'])}</p>""")

# JSON-LD support in shell
t = t.replace("def shell(title, desc, body, canonical, rel=\"\", noindex=False):",
              "def shell(title, desc, body, canonical, rel=\"\", noindex=False, ld=\"\"):")
t = t.replace("""<style>{CSS}</style></head>""", """{ld}<style>{CSS}</style></head>""")

new = '''
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
        "hasPart": [{"@type": "Article", "headline": s["title"], "url": f"{SITE}p/{s['_slug']}.html"} for s in items[:20]]}).replace("</", "<\\\\/") + "</script>"


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

'''
t = t.replace("# sitemap + robots + nostr identity (NIP-05)\nurls = [SITE]", new + "# sitemap + robots + nostr identity (NIP-05)\nurls = [SITE] + urls_extra")
t = t.replace("urls = [SITE] + urls_extra + [", "urls = [SITE] + urls_extra + [")
p.write_text(t, encoding="utf-8")
print("patched")
