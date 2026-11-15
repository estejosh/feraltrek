"""Plan item 8: tell search/feed discovery services the site changed. Best effort, never fails the run.
IndexNow (keyfile is public by design) + WebSub hub ping for each feed. Logs one line."""
import hashlib, json, re, sys, urllib.request, urllib.parse
from common import ROOT, CFG

BASE = CFG["site_url"].rstrip("/") + "/"
KEY = hashlib.sha256(b"feraltrek-indexnow").hexdigest()[:32]
DOCS = ROOT / "docs"


def post_json(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return type(e).__name__


def main():
    (DOCS / f"{KEY}.txt").write_text(KEY, encoding="utf-8")
    sm = (DOCS / "sitemap.xml")
    urls = re.findall(r"<loc>([^<]+)</loc>", sm.read_text(encoding="utf-8")) if sm.exists() else [BASE]
    urls = urls[:500]
    host = urllib.parse.urlparse(BASE).netloc
    st = post_json("https://api.indexnow.org/indexnow", {"host": host, "key": KEY, "keyLocation": BASE + KEY + ".txt", "urlList": urls})
    feeds = [BASE + "feeds/" + p.name for p in (DOCS / "feeds").glob("*.xml")]
    ws = []
    for f in feeds[:3]:
        data = urllib.parse.urlencode({"hub.mode": "publish", "hub.url": f}).encode()
        try:
            with urllib.request.urlopen(urllib.request.Request("https://pubsubhubbub.appspot.com/", data=data), timeout=15) as r:
                ws.append(r.status)
        except urllib.error.HTTPError as e:
            ws.append(e.code)
        except Exception as e:
            ws.append(type(e).__name__)
    print(f"pings: indexnow {len(urls)} urls -> {st}; websub {len(feeds[:3])} feeds -> {ws}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("pings failed:", e)
