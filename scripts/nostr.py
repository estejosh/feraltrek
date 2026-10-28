"""The project's own Nostr identity: key handling, BIP-340 signing (pure Python), publishing to relays.
The secret key lives only in data/private/nostr_key.json (gitignored) and a local backup copy."""
import hashlib, json, os, secrets, time
from common import ROOT, PRIVATE, load, save

KEY = PRIVATE / "nostr_key.json"
BACKUP = ROOT.parent.parent / "backups" / "feraltrek" / "nostr_key.json"   # X:\ferry\backups\feraltrek
PUBLIC = ROOT / "config" / "nostr_public.json"
RELAYS = ["wss://relay.damus.io", "wss://nos.lol", "wss://relay.primal.net", "wss://relay.nostr.band", "wss://nostr.mom"]

# --- secp256k1 / BIP-340 (reference algorithm) ---
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)


def _add(a, b):
    if a is None: return b
    if b is None: return a
    if a[0] == b[0] and a[1] != b[1]: return None
    lam = (3 * a[0] * a[0] * pow(2 * a[1], P - 2, P)) % P if a == b else ((b[1] - a[1]) * pow(b[0] - a[0], P - 2, P)) % P
    x = (lam * lam - a[0] - b[0]) % P
    return x, (lam * (a[0] - x) - a[1]) % P


def _mul(pt, k):
    r = None
    while k:
        if k & 1: r = _add(r, pt)
        pt, k = _add(pt, pt), k >> 1
    return r


def _th(tag, data):
    t = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(t + t + data).digest()


def pubkey(sk: bytes) -> bytes:
    return _mul(G, int.from_bytes(sk, "big"))[0].to_bytes(32, "big")


def sign(msg: bytes, sk: bytes) -> bytes:
    d = int.from_bytes(sk, "big")
    pt = _mul(G, d)
    d = d if pt[1] % 2 == 0 else N - d
    aux = secrets.token_bytes(32)
    t = (d ^ int.from_bytes(_th("BIP0340/aux", aux), "big")).to_bytes(32, "big")
    px = pt[0].to_bytes(32, "big")
    k = int.from_bytes(_th("BIP0340/nonce", t + px + msg), "big") % N
    R = _mul(G, k)
    k = k if R[1] % 2 == 0 else N - k
    e = int.from_bytes(_th("BIP0340/challenge", R[0].to_bytes(32, "big") + px + msg), "big") % N
    return R[0].to_bytes(32, "big") + ((k + e * d) % N).to_bytes(32, "big")


# --- bech32 (npub / nsec) ---
_C = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _polymod(v):
    g = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]; c = 1
    for x in v:
        b = c >> 25; c = (c & 0x1ffffff) << 5 ^ x
        for i in range(5): c ^= g[i] if (b >> i) & 1 else 0
    return c


def bech32(hrp, data: bytes):
    acc = bits = 0; five = []
    for b in data:
        acc = (acc << 8) | b; bits += 8
        while bits >= 5: bits -= 5; five.append((acc >> bits) & 31)
    if bits: five.append((acc << (5 - bits)) & 31)
    exp = [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]
    pm = _polymod(exp + five + [0] * 6) ^ 1
    return hrp + "1" + "".join(_C[d] for d in five + [(pm >> 5 * (5 - i)) & 31 for i in range(6)])


# --- identity ---
def identity():
    k = load(KEY, None)
    if not k:
        sk = secrets.token_bytes(32)
        pk = pubkey(sk)
        k = {"sk_hex": sk.hex(), "pk_hex": pk.hex(), "nsec": bech32("nsec", sk), "npub": bech32("npub", pk),
             "created": time.strftime("%Y-%m-%d")}
        save(KEY, k)
        save(BACKUP, k)
        save(PUBLIC, {"pk_hex": k["pk_hex"], "npub": k["npub"]})
    if not BACKUP.exists():
        save(BACKUP, k)
    return k


def event(kind, content, tags=()):
    k = identity()
    ev = {"pubkey": k["pk_hex"], "created_at": int(time.time()), "kind": kind, "tags": list(tags), "content": content}
    ser = json.dumps([0, ev["pubkey"], ev["created_at"], kind, ev["tags"], content], separators=(",", ":"), ensure_ascii=False)
    ev["id"] = hashlib.sha256(ser.encode()).hexdigest()
    ev["sig"] = sign(bytes.fromhex(ev["id"]), bytes.fromhex(k["sk_hex"])).hex()
    return ev


def publish(ev, relays=RELAYS):
    import websocket
    ok = []
    for url in relays:
        try:
            ws = websocket.create_connection(url, timeout=10)
            ws.send(json.dumps(["EVENT", ev]))
            deadline = time.time() + 8
            while time.time() < deadline:
                msg = json.loads(ws.recv())
                if msg[0] == "OK" and msg[1] == ev["id"]:
                    if msg[2]: ok.append(url)
                    break
            ws.close()
        except Exception:
            pass
    return ok
