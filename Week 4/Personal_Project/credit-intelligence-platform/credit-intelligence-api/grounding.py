"""Grounding helpers for Credit Intelligence RAG."""

REFUSAL = "The provided documents do not answer that question."


def build_context(hits: list[dict]) -> str:
    return "\n\n".join(f"[{hit['doc_id']}] {hit['title']}\n{hit['text']}" for hit in hits)


def is_refusal(answer: str) -> bool:
    return answer.strip().startswith(REFUSAL)