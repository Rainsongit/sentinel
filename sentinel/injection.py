"""Prompt-injection detection on three surfaces: the user's message, every
retrieved chunk and every tool result. Heuristic, no API call. Attempts to
make the model call one of the domain's own tools are caught too."""
import re
import unicodedata

PATTERNS = [
    (r"\b(ignore|disregard|forget|override)\b.{0,40}\b(instructions?|rules|prompt|guidelines|above)\b", 2),
    (r"\byou are now\b", 2),
    (r"\b(developer|god|admin|jailbreak|dan)\s+mode\b", 2),
    (r"\b(reveal|print|show|repeat|output)\b.{0,30}\b(system prompt|instructions|hidden prompt)\b", 2),
    (r"\bsystem prompt\b", 1),
    (r"^\s*(system|assistant)\s*:", 2),
    (r"<\|?(im_start|system|endoftext)\|?>", 2),
    (r"###\s*(system|instruction)", 2),
    (r"\bact as\b.{0,30}\b(admin|root|system|superuser)\b", 2),
    (r"\bpretend (to be|you are)\b", 1),
    (r"\bno (restrictions|rules|filters)\b", 1),
]
COMPILED = [(re.compile(p, re.IGNORECASE | re.MULTILINE), w) for p, w in PATTERNS]
ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"))


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(ZERO_WIDTH)
    return re.sub(r"\s+", " ", text)


def _tool_pattern(tool_names):
    if not tool_names:
        return None
    names = "|".join(map(re.escape, tool_names))
    return re.compile(rf"\b(call|invoke|run|execute|use)\b.{{0,30}}\b({names})\b", re.IGNORECASE)


def score(text: str, tool_names: list[str] | None = None) -> tuple[int, list[str]]:
    clean = normalize(text)
    matched = [(p.pattern, w) for p, w in COMPILED if p.search(clean)]
    tp = _tool_pattern(tool_names)
    if tp and tp.search(clean):
        matched.append(("tool-invocation", 2))
    return sum(w for _, w in matched), [m for m, _ in matched]


def is_injection(text: str, tool_names: list[str] | None = None, threshold: int = 2) -> bool:
    return score(text, tool_names)[0] >= threshold
