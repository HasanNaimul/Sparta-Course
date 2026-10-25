"""Retrieval backend for Credit Intelligence."""

import chunk_index
import hybrid
import knowledge

CHUNK_STRATEGY = "title_contextual_100"
SEARCH_MODE = "hybrid"

# Keep local as the validated baseline until Azure evaluation is complete.
SEARCH_BACKEND = "azure"


def count() -> int:
    if SEARCH_BACKEND == "azure":
        import azure_store
        return azure_store.count()

    return chunk_index.count(CHUNK_STRATEGY)


def build_index() -> int:
    if SEARCH_BACKEND == "azure":
        raise RuntimeError("The app only reads the Azure index. Build it with: python -m azure_build")

    return chunk_index.build(CHUNK_STRATEGY)


def search(question: str, top_k: int = 5) -> list[dict]:
    query_vectors, _ = knowledge.embed_texts([question], input_type="query")

    if SEARCH_BACKEND == "azure":
        import azure_store
        return azure_store.search_with_vector(question, query_vectors[0], top_k)

    if count() == 0:
        raise RuntimeError("Index is empty. Build the knowledge index first.")

    if SEARCH_MODE == "hybrid":
        return hybrid.search_with_vector(question, query_vectors[0], top_k, strategy=CHUNK_STRATEGY)

    return chunk_index.search_with_vector(query_vectors[0], top_k, strategy=CHUNK_STRATEGY)