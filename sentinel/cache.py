"""Semantic cache. Namespaced by role so a higher role's answer is never served
to a lower role. Only caches answers that used no tools (tool data is live)."""
import time
import numpy as np
from sentinel import embed
from sentinel.config import CACHE_THRESHOLD, CACHE_TTL_SECONDS


class SemanticCache:
    def __init__(self, threshold: float = CACHE_THRESHOLD, ttl: int = CACHE_TTL_SECONDS):
        self.threshold, self.ttl = threshold, ttl
        self.entries: dict[str, list[dict]] = {}

    def get(self, role: str, question: str) -> dict | None:
        now = time.time()
        entries = [e for e in self.entries.get(role, []) if now - e["t"] < self.ttl]
        self.entries[role] = entries
        if not entries:
            return None
        q = embed.encode([question])[0]
        sims = np.array([e["vec"] @ q for e in entries])
        best = int(np.argmax(sims))
        return entries[best]["value"] if sims[best] >= self.threshold else None

    def put(self, role: str, question: str, value: dict) -> None:
        vec = embed.encode([question])[0]
        self.entries.setdefault(role, []).append({"vec": vec, "value": value, "t": time.time()})
