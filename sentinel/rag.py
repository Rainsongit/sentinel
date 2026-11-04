"""Role-filtered retrieval over the domain's docs. Each doc declares
`min_role:` in front matter. Chunks above the caller's role are never scored.
Retrieved chunks are scanned for indirect prompt injection."""
import re
import numpy as np
from sentinel import domain, embed, injection, rbac
from sentinel.config import TOP_K


def load_chunks(cfg: dict) -> list[dict]:
    chunks = []
    for path in sorted((cfg["dir"] / "docs").glob("*.md")):
        raw = path.read_text()
        min_role = re.search(r"^min_role:\s*(\w+)", raw, re.M).group(1)
        rbac.level(min_role, cfg)  # fail fast on a typo'd role
        body = re.sub(r"^---.*?---\s*", "", raw, flags=re.S)
        for i, para in enumerate(p.strip() for p in body.split("\n\n") if p.strip()):
            chunks.append({"id": f"{path.stem}:{i}", "doc": path.stem,
                           "min_role": min_role, "text": para})
    return chunks


class Retriever:
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or domain.current()
        self.chunks = load_chunks(self.cfg)
        self.vectors = embed.encode([c["text"] for c in self.chunks])
        self.tool_names = list(self.cfg["tools"])

    def search(self, query: str, role: str, k: int = TOP_K) -> tuple[list[dict], int]:
        allowed = [i for i, c in enumerate(self.chunks) if rbac.can_read(role, c["min_role"], self.cfg)]
        if not allowed:
            return [], 0
        q = embed.encode([query])[0]
        scores = self.vectors[allowed] @ q
        results, dropped = [], 0
        for j in np.argsort(-scores)[:k]:
            chunk = self.chunks[allowed[j]]
            if injection.is_injection(chunk["text"], self.tool_names):
                dropped += 1
                continue
            results.append({**chunk, "score": float(scores[j])})
        return results, dropped
