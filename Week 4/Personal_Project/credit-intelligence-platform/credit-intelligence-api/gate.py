"""Decide whether a retrieved chunk is relevant enough to reach the model."""


def is_usable(hit: dict, cosine_floor: float) -> bool:
    if hit.get("exact_match", False):
        return True

    score = hit.get("score")

    if score is None:
        return False

    return score >= cosine_floor