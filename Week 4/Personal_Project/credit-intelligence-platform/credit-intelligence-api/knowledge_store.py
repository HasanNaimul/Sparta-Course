"""Retrieval backend for Credit Intelligence."""

import chunk_index
import hybrid
import knowledge

SEARCH_MODE = "hybrid"


def count() -> int:
    return chunk_index.count()


def build_index() -> int:
    """Build the local Chroma index and return embedding-token usage."""
    return chunk_index.build()


def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed a question and search using the selected retrieval mode."""
    if count() == 0:
        raise RuntimeError("Index is empty. Build the knowledge index first.")

    query_vectors, _ = knowledge.embed_texts([question], input_type="query")

    if SEARCH_MODE == "hybrid":
        return hybrid.search_with_vector(question, query_vectors[0], top_k)

    return chunk_index.search_with_vector(query_vectors[0], top_k)