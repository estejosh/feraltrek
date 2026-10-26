"""List proposals that have no summary yet (oldest first)."""
from common import ROOT, load

props = [load(f, {}) for f in (ROOT / "data" / "proposals").glob("*.json")]
done = {f.stem for f in (ROOT / "data" / "summaries").glob("*.json")}
todo = sorted((p for p in props if p["id"] not in done), key=lambda p: p["created"])
for p in todo:
    print(f"{p['id']}\t{p['space']['id']}\t{p['title'][:90]}")
print(f"# {len(todo)} pending")
