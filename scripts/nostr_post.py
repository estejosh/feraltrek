"""Post new summaries to Nostr as the project (a few per run, newest first). --profile republishes the profile."""
import sys, re, time
from common import ROOT, CFG, PRIVATE, load, save
import nostr

SITE = CFG["site_url"].rstrip("/") + "/"
posted = load(PRIVATE / "nostr_posted.json", [])
k = nostr.identity()

if "--profile" in sys.argv or not posted:
    meta = {"name": "Governance Digest", "display_name": "Governance Digest",
            "about": "What DAOs are proposing and discussing, in plain English. Aave, Uniswap, Arbitrum, ENS, Lido and more. "
                     "Facts only, not advice. Run by an autonomous AI project; code and revenue are public.",
            "website": SITE, "nip05": "digest@" + re.sub(r"^https?://", "", SITE).split("/")[0] if SITE.count("/") <= 3 else ""}
    ev = nostr.event(0, __import__("json").dumps(meta))
    print("profile ->", nostr.publish(ev))

sums = [load(f, {}) for f in (ROOT / "data" / "summaries").glob("*.json")]
props = {f.stem: load(f, {}) for f in (ROOT / "data" / "proposals").glob("*.json")}
todo = sorted((s for s in sums if not s.get("skip") and s["id"] not in posted),
              key=lambda s: props.get(s["id"], {}).get("created", 0), reverse=True)
limit = 6
for s in todo[:limit]:
    slug = re.sub(r"[^a-z0-9]+", "-", f"{s['space']} {s['title']}".lower()).strip("-")[:80] + "-" + s["id"][-6:]
    dao = s["space"].replace(".eth", "").split("-")[0].replace("uniswapgovernance", "uniswap").replace("arbitrumfoundation", "arbitrum")
    content = f"{s['title']} ({dao})\n\n{s['headline']}\n\n{SITE}p/{slug}.html\n\n#DAO #governance #{dao}"
    ev = nostr.event(1, content, [["t", "dao"], ["t", "governance"], ["t", dao], ["r", SITE]])
    relays = nostr.publish(ev)
    if relays:
        posted.append(s["id"])
        save(PRIVATE / "nostr_posted.json", posted)
    print(f"{'ok' if relays else 'FAILED'} {len(relays)} relays: {s['title'][:60]}")
    time.sleep(3)
print(f"nostr: posted {min(limit, len(todo))} of {len(todo)} pending; npub {k['npub']}")
