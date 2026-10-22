"""Retrieval backend for Credit Intelligence."""

import chunk_index
import hybrid
import knowledge

CHUNK_STRATEGY = "title_contextual_100"
SEARCH_MODE = "hybrid"


def count() -> int:
    return chunk_index.count(CHUNK_STRATEGY)


def build_index() -> int:
    return chunk_index.build(CHUNK_STRATEGY)


def search(question: str, top_k: int = 3) -> list[dict]:
    if count() == 0:
        raise RuntimeError("Index is empty. Build the knowledge index first.")

    query_vectors, _ = knowledge.embed_texts([question], input_type="query")

    if SEARCH_MODE == "hybrid":
        return hybrid.search_with_vector(question, query_vectors[0], top_k, strategy=CHUNK_STRATEGY)

    return chunk_index.search_with_vector(query_vectors[0], top_k, strategy=CHUNK_STRATEGY)