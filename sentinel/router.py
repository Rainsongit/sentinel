"""Cost-aware model router. Simple lookups go to the small model; multi-step,
analytical or action-taking requests go to the large one."""
import re
from sentinel.config import LARGE_MODEL, SMALL_MODEL

COMPLEX = re.compile(
    r"\b(compare|explain why|analy[sz]e|trade-?offs?|recommend|which is better|pros and cons|"
    r"summari[sz]e|step[- ]by[- ]step|plan)\b", re.IGNORECASE)
ACTION = re.compile(r"\b(create|submit|place|request|update)\b", re.IGNORECASE)


def route(question: str) -> tuple[str, str]:
    words = len(question.split())
    if COMPLEX.search(question):
        return LARGE_MODEL, "complex reasoning"
    if ACTION.search(question):
        return LARGE_MODEL, "takes an action"
    if words > 35 or question.count("?") > 1:
        return LARGE_MODEL, "long or multi-part"
    return SMALL_MODEL, "simple lookup"
