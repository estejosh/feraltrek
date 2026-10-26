"""Read USDC transfers to the pay address on Base, match them to tx hashes emailed to the inbox,
and grant digest access to the sender. Public chain data only; no keys."""
import re, time, datetime as dt, requests
from email.utils import parseaddr
from common import CFG, PRIVATE, load, save
import agentmail

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ADDR = CFG["pay_address"].lower()
HASH = re.compile(r"0x[0-9a-fA-F]{64}")
STATE, SUBS = PRIVATE / "payments.json", PRIVATE / "subscribers.json"


RPCS = [CFG["rpc"], "https://base-rpc.publicnode.com", "https://base.llamarpc.com"]


def rpc(method, params):
    """Public RPCs rate-limit; slow down, retry, and fall back."""
    err = None
    for attempt in range(6):
        url = RPCS[attempt % len(RPCS)]
        try:
            j = requests.post(url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=60).json()
            if "error" not in j:
                time.sleep(0.4)
                return j["result"]
            err = j["error"]
        except Exception as e:
            err = e
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(err)


st = load(STATE, {"last_block": None, "transfers": {}, "used_tx": [], "seen_msgs": []})
subs = load(SUBS, {})

# 1. new incoming USDC transfers
head = int(rpc("eth_blockNumber", []), 16)
b = st["last_block"] + 1 if st["last_block"] else head - 5_000
to_topic = "0x" + "0" * 24 + ADDR[2:]
while b <= head:
    e = min(b + 1999, head)
    for lg in rpc("eth_getLogs", [{"address": CFG["usdc_contract"], "topics": [TRANSFER, None, to_topic],
                                   "fromBlock": hex(b), "toBlock": hex(e)}]):
        st["transfers"][lg["transactionHash"].lower()] = {
            "from": "0x" + lg["topics"][1][-40:], "usdc": int(lg["data"], 16) / 1e6, "block": int(lg["blockNumber"], 16)}
    b = e + 1
st["last_block"] = head

# 2. emails carrying tx hashes
now = dt.datetime.now(dt.timezone.utc)
granted = 0
for m in agentmail.list_messages():
    mid = m["message_id"]
    if mid in st["seen_msgs"] or "received" not in (m.get("labels") or []):
        continue
    full = agentmail.get_message(mid)
    text = " ".join(str(full.get(k) or "") for k in ("subject", "text", "html"))
    hashes = {h.lower() for h in HASH.findall(text)}
    sender = parseaddr(full.get("from") or "")[1].lower()
    if not hashes:
        st["seen_msgs"].append(mid)  # ordinary mail, nothing to do
        continue
    age_days = (now - dt.datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00"))).days
    matched = [h for h in hashes if h in st["transfers"] and h not in st["used_tx"]]
    if not matched:
        if age_days >= 3:
            agentmail.reply(mid, "We could not find a USDC payment on Base to "
                            f"{CFG['pay_address']} matching that transaction hash. "
                            "If this is a mistake, reply with the correct hash.")
            st["seen_msgs"].append(mid)
        continue  # chain may lag; retry next run
    usdc = sum(st["transfers"][h]["usdc"] for h in matched)
    days = int(usdc / CFG["price_usdc"] * CFG["days_per_price"])
    cur = subs.get(sender, {}).get("paid_until")
    base = max(now, dt.datetime.fromisoformat(cur)) if cur else now
    until = base + dt.timedelta(days=days)
    subs[sender] = {"paid_until": until.isoformat(), "paid_total": subs.get(sender, {}).get("paid_total", 0) + usdc}
    st["used_tx"] += matched
    st["seen_msgs"].append(mid)
    agentmail.reply(mid, f"Payment received: {usdc:g} USDC. Your Governance Digest access runs until "
                    f"{until.date().isoformat()}. The full weekly digest goes to this address.")
    granted += 1

save(STATE, st)
save(SUBS, subs)
print(f"head {head}, transfers known {len(st['transfers'])}, granted {granted}, active subs "
      f"{sum(1 for s in subs.values() if dt.datetime.fromisoformat(s['paid_until']) > now)}")
