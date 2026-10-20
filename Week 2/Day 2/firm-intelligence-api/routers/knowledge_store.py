# Embedded texts are imported, not rewritten.
# The embedding provider has not changed, only where the vectors get stored.

import chunk_index
import hybrid
import knowledge


# Our chosen chunking strategy.
CHUNK_STRATEGY = "sections_contextual"

# Choose which local retrieval system the app uses.
SEARCH_MODE = "hybrid"

# Set to "local" or "azure".
SEARCH_BACKEND = "local"


def count() -> int:
    if SEARCH_BACKEND == "azure":
        import azure_store
        return azure_store.count()

    return chunk_index.collection_for(CHUNK_STRATEGY).count()


def build_index() -> int:
    """Build the local index. Azure is built separately with python -m azure_build."""
    if SEARCH_BACKEND == "azure":
        raise RuntimeError(
            "The app only reads the Azure index. Build it with: python -m azure_build"
        )

    return chunk_index.build(CHUNK_STRATEGY)["embedding_tokens"]


def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question and search using the selected retrieval backend."""
    if count() == 0:
        if SEARCH_BACKEND == "azure":
            raise RuntimeError(
                "The Azure index is empty or missing. Build it with: python -m azure_build"
            )

        raise RuntimeError(
            "Index is empty, call POST /knowledge/index first"
        )

    query_vectors, _ = knowledge.embed_texts([question], input_type="query")

    if SEARCH_BACKEND == "azure":
        import azure_store
        return azure_store.search_with_vector(question, query_vectors[0], top_k)

    if SEARCH_MODE == "hybrid":
        return hybrid.search_with_vector(
            CHUNK_STRATEGY,
            question,
            query_vectors[0],
            top_k,
        )

    return chunk_index.search_with_vectors(
        CHUNK_STRATEGY,
        query_vectors,
        k=top_k,
    )[0]