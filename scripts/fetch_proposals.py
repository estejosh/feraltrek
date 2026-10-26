"""Pull recent Snapshot proposals and new DAO forum topics into data/proposals/."""
import time, re, html, datetime as dt, requests
from common import ROOT, CFG, save

OUT = ROOT / "data" / "proposals"
UA = {"User-Agent": "feraltrek-digest (+https://github.com/estejosh/feraltrek)"}
since = int(time.time()) - CFG["lookback_days"] * 86400
new = 0


def keep(item):
    global new
    f = OUT / f"{item['file']}.json"
    if not f.exists():
        new += 1
    save(f, item)


# Snapshot (votes)
Q = """query($spaces:[String],$since:Int){proposals(first:100,orderBy:"created",orderDirection:desc,
 where:{space_in:$spaces,created_gte:$since}){id title body state start end created choices scores scores_total
 link discussion author space{id name}}}"""
r = requests.post("https://hub.snapshot.org/graphql", headers=UA, timeout=60,
                  json={"query": Q, "variables": {"spaces": CFG["spaces"], "since": since}})
r.raise_for_status()
for p in r.json()["data"]["proposals"]:
    p.update(source="snapshot", file=p["id"],
             link=f"https://snapshot.org/#/{p['space']['id']}/proposal/{p['id']}")
    keep(p)

# DAO forums (discussion, before it reaches a vote)
for name, base in CFG["forums"].items():
    try:
        topics = requests.get(f"{base}/latest.json", headers=UA, timeout=30).json()["topic_list"]["topics"]
    except Exception as e:
        print(f"forum {name}: skipped ({str(e)[:60]})")
        continue
    for t in topics:
        created = int(dt.datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")).timestamp())
        if t.get("pinned") or created < since:
            continue
        fid = f"forum-{name}-{t['id']}"
        if (OUT / f"{fid}.json").exists():
            continue  # forum posts do not change state; fetch once
        try:
            post = requests.get(f"{base}/t/{t['id']}.json", headers=UA, timeout=30).json()["post_stream"]["posts"][0]
            body = html.unescape(re.sub(r"<[^>]+>", " ", post["cooked"]))
            body = re.sub(r"\s+", " ", body).strip()[:12000]
        except Exception:
            body = ""
        keep({"id": fid, "file": fid, "source": "forum", "title": t["title"], "body": body,
              "created": created, "state": "discussion", "space": {"id": name, "name": name},
              "link": f"{base}/t/{t['slug']}/{t['id']}"})
        time.sleep(0.5)

print(f"new items: {new}")
