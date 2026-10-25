"""Decide whether a retrieved chunk is relevant enough to reach the model."""


def is_usable(hit: dict, cosine_floor: float, rerank_floor: float = 2.0) -> bool:
    if hit.get("reranker_score") is not None:
        return hit["reranker_score"] >= rerank_floor

    if hit.get("exact_match", False):
        return True

    score = hit.get("score")
    return score is not None and score >= cosine_floor