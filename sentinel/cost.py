from sentinel.config import LARGE_MODEL, PRICES


def cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pin, pout = PRICES.get(model, PRICES[LARGE_MODEL])
    return (prompt_tokens * pin + completion_tokens * pout) / 1_000_000


def baseline_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """What the same tokens would cost if everything went to the large model."""
    return cost(LARGE_MODEL, prompt_tokens, completion_tokens)
