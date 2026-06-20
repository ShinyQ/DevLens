from devlens.config import settings


def compute_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> float:
    matched_key = _match_model(model)
    if not matched_key:
        return 0.0

    p = settings.pricing[matched_key]
    cost = (input_tokens / 1_000_000) * p["input"]
    cost += (output_tokens / 1_000_000) * p["output"]
    cost += (cache_creation_tokens / 1_000_000) * p["input"] * settings.cache_creation_multiplier
    cost += (cache_read_tokens / 1_000_000) * p["input"] * settings.cache_read_multiplier
    return cost


def _match_model(model: str) -> str | None:
    if not model:
        return None
    model_lower = model.lower()
    # Check longer keys first to avoid false prefix matches
    sorted_keys = sorted(settings.pricing.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key in model_lower:
            return key
    return None
