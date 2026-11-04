"""Loads the active domain plug-in from domains/<name>/domain.json.
Pick the domain with the DOMAIN env var (default: hr)."""
import json
import os
from functools import lru_cache
from sentinel.config import DOMAINS_DIR

REQUIRED = ["assistant", "roles", "api_keys", "tools", "mcp_server"]


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    path = DOMAINS_DIR / name / "domain.json"
    if not path.exists():
        raise FileNotFoundError(f"no domain config at {path}")
    cfg = json.loads(path.read_text())
    missing = [k for k in REQUIRED if k not in cfg]
    if missing:
        raise ValueError(f"{path} is missing {missing}")
    unknown = {r for r in cfg["tools"].values()} - set(cfg["roles"])
    if unknown:
        raise ValueError(f"{path}: tools reference unknown roles {unknown}")
    cfg.setdefault("canaries", {})
    cfg.setdefault("leak_markers", {})
    cfg.setdefault("handoff", None)
    cfg["name"], cfg["dir"] = name, DOMAINS_DIR / name
    return cfg


def current() -> dict:
    return load(os.getenv("DOMAIN", "hr"))
