"""Shared helpers. Paths are relative to the repo root."""
import json, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "config" / "project.json").read_text(encoding="utf-8"))
PRIVATE = ROOT / "data" / "private"
PRIVATE.mkdir(parents=True, exist_ok=True)


def load(path, default):
    p = pathlib.Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def save(path, obj):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, p)


def env(key):
    """Read a key from .env without printing it."""
    if key in os.environ:
        return os.environ[key]
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"')
    raise KeyError(key)
