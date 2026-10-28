"""Email the weekly paid digest: votes closing in the next 7 days (with deadlines) first, then every item
from the past week in full. Runs on CFG['email_day'] or with --force; --dry sends nothing.
Each subscriber gets their own email (no shared recipient lists)."""
import sys, html, datetime as dt
from common import ROOT, CFG, PRIVATE, load, save
import agentmail

E = html.escape
now = dt.datetime.now(dt.timezone.utc)
force, dry = "--force" in sys.argv, "--dry" in sys.argv
st = load(PRIVATE / "digest.json", {"last_sent": None})
if not force and now.strftime("%A") != CFG["email_day"]:
    print("not digest day"); sys.exit(0)
if st["last_sent"] == now.date().isoformat() and not force:
    print("already sent today"); sys.exit(0)

props = {f.stem: load(f, {}) for f in (ROOT / "data" / "proposals").glob("*.json")}
sums = {s["id"]: s for s in (load(f, {}) for f in (ROOT / "data" / "summaries").glob("*.json")) if not s.get("skip")}
soon = now + dt.timedelta(days=7)
closing = sorted((p for p in props.values() if p.get("source") == "snapshot" and p.get("state") == "active"
                  and now.timestamp() < (p.get("end") or 0) <= soon.timestamp()), key=lambda p: p["end"])
since = (now - dt.timedelta(days=7)).date().isoformat()
items = [s for s in sums.values() if s.get("written", "") >= since]
if not items and not closing:
    print("nothing this week"); sys.exit(0)


def when(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%a %b %d, %H:%M UTC")


t, h = [f"Governance Digest, week of {now.date().isoformat()}\n"], []
if closing:
    t.append("VOTES CLOSING IN THE NEXT 7 DAYS")
    h.append("<h2>Votes closing in the next 7 days</h2><ul>")
    for p in closing:
        line = f"{when(p['end'])}: {p['title']} ({p['space']['id']})"
        t.append(f"- {line}\n  {p['link']}")
        h.append(f"<li><b>{E(when(p['end']))}</b>: <a href='{E(p['link'])}'>{E(p['title'])}</a> ({E(p['space']['id'])})"
                 + (f"<br><small>{E(sums[p['id']]['headline'])}</small>" if p["id"] in sums else "") + "</li>")
    h.append("</ul>")
    t.append("")
if items:
    t.append("THIS WEEK IN FULL")
    h.append("<h2>This week in full</h2>")
    for s in items:
        flags = ", ".join(s.get("risk_flags", []))
        t.append(f"{s['title']} ({s['space']})\n{s['summary']}\nFlags: {flags}\nStatus: {s.get('vote','')}\n{s['url']}\n")
        h.append(f"<h3><a href='{E(s['url'])}'>{E(s['title'])}</a> <small>({E(s['space'])})</small></h3><p>{E(s['summary'])}</p>"
                 f"<p><small>Flags: {E(flags)}<br>Status: {E(s.get('vote',''))}</small></p>")
t.append("Facts only, not advice. Reply to this email with questions.")
text = "\n".join(t)
page = f"<div style='font-family:Georgia,serif;max-width:640px'><h1>Governance Digest</h1>{''.join(h)}<p><small>Facts only, not advice.</small></p></div>"

subs = load(PRIVATE / "subscribers.json", {})
active = [e for e, s in subs.items() if dt.datetime.fromisoformat(s["paid_until"]) > now]
subject = f"Governance Digest: {len(closing)} votes closing, {len(items)} new items"
for e in active:
    if not dry:
        agentmail.send(e, subject, text, page)
if not dry:
    st["last_sent"] = now.date().isoformat()
    save(PRIVATE / "digest.json", st)
print(f"digest: {len(closing)} closing, {len(items)} items, {len(active)} recipients{' (dry run)' if dry else ''}")
