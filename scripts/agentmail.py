"""Tiny AgentMail client (REST). Key from .env AGENT_MAIL_API_KEY."""
import urllib.parse, requests
from common import CFG, env

BASE = "https://api.agentmail.to/v0"
INBOX = urllib.parse.quote(CFG["inbox"], safe="")


def _h():
    return {"Authorization": f"Bearer {env('AGENT_MAIL_API_KEY')}"}


def list_messages(limit=100):
    r = requests.get(f"{BASE}/inboxes/{INBOX}/messages", headers=_h(), params={"limit": limit}, timeout=60)
    r.raise_for_status()
    return r.json().get("messages", [])


def get_message(message_id):
    mid = urllib.parse.quote(message_id, safe="")
    r = requests.get(f"{BASE}/inboxes/{INBOX}/messages/{mid}", headers=_h(), timeout=60)
    r.raise_for_status()
    return r.json()


def send(to, subject, text, html=None):
    body = {"to": [to], "subject": subject, "text": text}
    if html:
        body["html"] = html
    r = requests.post(f"{BASE}/inboxes/{INBOX}/messages/send", headers=_h(), json=body, timeout=60)
    r.raise_for_status()
    return r.json()


def reply(message_id, text):
    mid = urllib.parse.quote(message_id, safe="")
    r = requests.post(f"{BASE}/inboxes/{INBOX}/messages/{mid}/reply", headers=_h(), json={"text": text}, timeout=60)
    r.raise_for_status()
    return r.json()
