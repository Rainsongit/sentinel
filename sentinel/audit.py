"""Append-only audit log. PII is redacted before anything is written."""
import json
import time
from sentinel.config import LOG_DIR
from sentinel.guardrails import redact_pii


def log(event: dict) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    event = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **event}
    line, _ = redact_pii(json.dumps(event))
    with open(LOG_DIR / "audit.jsonl", "a") as f:
        f.write(line + "\n")
