"""Input and output guardrails: PII redaction, optional domain handoff rule
(e.g. legal or medical questions routed to a human), and canary-token leak
detection on outputs."""
import re
from sentinel import domain, rbac

PII_PATTERNS = {
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "CARD": r"\b(?:\d[ -]?){13,16}\b",
    "EMAIL": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
    "PHONE": r"\b(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]?\d{3}[ .-]?\d{4}\b",
}
LEAK_BLOCK = "That information isn't available for your access level."


def redact_pii(text: str) -> tuple[str, int]:
    count = 0
    for label, pattern in PII_PATTERNS.items():
        text, n = re.subn(pattern, f"[{label}]", text)
        count += n
    return text, count


def handoff(role: str, text: str, cfg: dict | None = None) -> str | None:
    """Returns the handoff message if this question must go to a human."""
    rule = (cfg or domain.current())["handoff"]
    if rule and role in rule["roles"] and re.search(rule["pattern"], text, re.IGNORECASE):
        return rule["message"]
    return None


def check_output(role: str, text: str, cfg: dict | None = None) -> tuple[str, bool]:
    """Returns (safe_text, leaked). Canary tokens are planted in restricted data;
    one appearing for a role below its level means a leak."""
    cfg = cfg or domain.current()
    for canary, min_role in cfg["canaries"].items():
        if canary in text and not rbac.can_read(role, min_role, cfg):
            return LEAK_BLOCK, True
    for canary in cfg["canaries"]:
        text = text.replace(canary, "")
    text, _ = redact_pii(text)
    return text, False
