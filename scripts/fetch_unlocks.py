"""Fetch token unlock schedules from DefiLlama's free emissions datasets (no key).

Writes data/unlocks/<slug>.json (strings and numbers only) and data/unlocks/index.json.
Never crashes the daily run: any bad token is logged and skipped.
Source notes: log/unlocks_sources.md
"""
import json, sys, time, datetime, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from common import ROOT, save

OUT = ROOT / "data" / "unlocks"
BASE = "https://defillama-datasets.llama.fi/"
PRICES = "https://coins.llama.fi/prices/current/"
TIMEOUT = 20
HORIZON_DAYS = 400  # keep events up to this far ahead
MAX_EVENTS = 60


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "feraltrek/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.load(r)


def iso(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d")


def one(slug):
    try:
        d = get(BASE + "emissions/" + urllib.parse.quote(slug))
        meta = d.get("metadata") or {}
        now = time.time()
        by_ts = {}
        for e in meta.get("events") or []:
            ts = e.get("timestamp")
            if isinstance(ts, list):
                ts = ts[0] if ts else None
            if not isinstance(ts, (int, float)):
                continue
            if ts < now or ts > now + HORIZON_DAYS * 86400:
                continue
            n = e.get("noOfTokens") or [0]
            try:
                amt = float(n[0])
            except Exception:
                continue
            row = by_ts.setdefault(int(ts), {"tokens": 0.0, "groups": [], "types": set()})
            row["tokens"] += amt
            cat = str(e.get("category") or "")
            if cat and cat not in row["groups"]:
                row["groups"].append(cat)
            row["types"].add(str(e.get("unlockType") or ""))
        events = []
        for ts in sorted(by_ts)[:MAX_EVENTS]:
            r = by_ts[ts]
            events.append({
                "ts": ts, "date": iso(ts), "tokens": round(r["tokens"], 2),
                "groups": ", ".join(r["groups"]), "type": "/".join(sorted(t for t in r["types"] if t)),
            })
        sm = d.get("supplyMetrics") or {}
        return {
            "slug": slug, "name": str(d.get("name") or slug),
            "price_id": str(meta.get("token") or ""),
            "max_supply": meta.get("total") or sm.get("maxSupply") or 0,
            "link": "https://defillama.com/unlocks/" + slug,
            "source": BASE + "emissions/" + slug,
            "events": events,
        }
    except Exception as ex:
        print("skip", slug, type(ex).__name__, str(ex)[:80])
        return None


def prices(ids):
    out = {}
    ids = sorted(set(i for i in ids if i))
    for i in range(0, len(ids), 40):
        chunk = ids[i:i + 40]
        try:
            d = get(PRICES + ",".join(chunk))
            for k, v in (d.get("coins") or {}).items():
                if isinstance(v, dict) and isinstance(v.get("price"), (int, float)):
                    out[k] = v["price"]
        except Exception as ex:
            print("price chunk failed", type(ex).__name__, str(ex)[:80])
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        slugs = get(BASE + "emissionsProtocolsList")
    except Exception as ex:
        print("token list failed", ex)
        return 0
    with ThreadPoolExecutor(8) as ex:
        rows = [r for r in ex.map(one, slugs) if r]
    px = prices([r["price_id"] for r in rows])
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    index = []
    for r in rows:
        if not r["events"]:
            continue
        p = px.get(r["price_id"])
        r["price_usd"] = p if p is not None else ""
        r["fetched"] = today
        for e in r["events"]:
            e["usd"] = round(e["tokens"] * p, 2) if p is not None else ""
            e["pct_of_max"] = round(100.0 * e["tokens"] / r["max_supply"], 3) if r["max_supply"] else ""
        save(OUT / (r["slug"] + ".json"), r)
        nxt = r["events"][0]
        index.append({"slug": r["slug"], "name": r["name"], "next_date": nxt["date"], "next_tokens": nxt["tokens"],
                      "next_usd": nxt["usd"], "next_pct_of_max": nxt["pct_of_max"], "events": len(r["events"])})
    index.sort(key=lambda x: x["next_date"])
    save(OUT / "index.json", {"fetched": today, "count": len(index), "tokens": index})
    print("fetched", len(rows), "tokens;", len(index), "with future events;",
          sum(1 for i in index if i["next_usd"] != ""), "priced")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as ex:
        print("fetch_unlocks failed:", ex)
        sys.exit(0)
