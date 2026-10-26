"""Email the weekly full digest to paid subscribers. Runs on CFG['email_day'] or with --force.
Each subscriber gets their own email (no shared recipient lists)."""
import sys, html, datetime as dt
from common import ROOT, CFG, PRIVATE, load, save
import agentmail

now = dt.datetime.now(dt.timezone.utc)
force = "--force" in sys.argv
dry = "--dry" in sys.argv
st = load(PRIVATE / "digest.json", {"last_sent": None})
if not force and now.strftime("%A") != CFG["email_day"]:
    print("not digest day"); sys.exit(0)
if st["last_sent"] == now.date().isoformat() and not force:
    print("already sent today"); sys.exit(0)

since = (now - dt.timedelta(days=7)).date().isoformat()
items = [s for s in (load(f, {}) for f in (ROOT / "data" / "summaries").glob("*.json"))
         if not s.get("skip") and s.get("written", "") >= since]
if not items:
    print("nothing new this week"); sys.exit(0)

txt = [f"Governance Digest, week of {since}\n"]
for s in items:
    flags = ", ".join(s.get("risk_flags", []))
    txt.append(f"{s['title']} ({s['space']})\n{s['summary']}\nFlags: {flags}\nVote: {s.get('vote','')}\n{s['url']}\n")
txt.append("Facts only, not advice. Reply to this email with questions.")
text = "\n".join(txt)
body = "".join(f"<h3><a href='{html.escape(s['url'])}'>{html.escape(s['title'])}</a> <small>({html.escape(s['space'])})</small></h3>"
               f"<p>{html.escape(s['summary'])}</p><p><small>Flags: {html.escape(', '.join(s.get('risk_flags', [])))}"
               f"<br>Vote: {html.escape(s.get('vote',''))}</small></p>" for s in items)
page = f"<div style='font-family:Georgia,serif;max-width:640px'><h2>Governance Digest</h2>{body}<p><small>Facts only, not advice.</small></p></div>"

subs = load(PRIVATE / "subscribers.json", {})
active = [e for e, s in subs.items() if dt.datetime.fromisoformat(s["paid_until"]) > now]
for e in active:
    if dry:
        print("would send to one subscriber"); continue
    agentmail.send(e, f"Governance Digest: {len(items)} items this week", text, page)
if not dry:
    st["last_sent"] = now.date().isoformat()
    save(PRIVATE / "digest.json", st)
print(f"digest: {len(items)} items, {len(active)} recipients{' (dry run)' if dry else ''}")
