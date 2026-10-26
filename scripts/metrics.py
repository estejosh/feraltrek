"""Write metrics.json (public, no personal data) for the un-drifter."""
import datetime as dt
from common import ROOT, PRIVATE, load, save

now = dt.datetime.now(dt.timezone.utc)
pay = load(PRIVATE / "payments.json", {"transfers": {}, "used_tx": []})
subs = load(PRIVATE / "subscribers.json", {})
sums = [load(f, {}) for f in (ROOT / "data" / "summaries").glob("*.json")]
week = (now - dt.timedelta(days=7)).date().isoformat()
m = {
    "updated": now.isoformat(timespec="seconds"),
    "usdc_received_total": round(sum(t["usdc"] for t in pay["transfers"].values()), 2),
    "payments_total": len(pay["transfers"]),
    "payments_unmatched": len(set(pay["transfers"]) - set(pay["used_tx"])),
    "subscribers_active": sum(1 for s in subs.values() if dt.datetime.fromisoformat(s["paid_until"]) > now),
    "subscribers_ever": len(subs),
    "items_published_total": sum(1 for s in sums if not s.get("skip")),
    "items_published_7d": sum(1 for s in sums if not s.get("skip") and s.get("written", "") >= week),
}
save(ROOT / "metrics.json", m)
print(m)
