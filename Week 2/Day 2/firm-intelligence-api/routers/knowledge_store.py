# Embedded texts are imported, not rewritten.
# The embedding provider has not changed, only where the vectors get stored.

import knowledge
import chunk_index
import hybrid


# Our chosen chunking strategy.
CHUNK_STRATEGY = "sections_contextual"

# Choose which retrieval system the app uses.
SEARCH_MODE = "hybrid"


def count() -> int:
    return chunk_index.collection_for(CHUNK_STRATEGY).count()


def build_index() -> int:
    """Chunk and embed the corpus. Free if nothing has changed since the last build."""
    return chunk_index.build(CHUNK_STRATEGY)["embedding_tokens"]


def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question and search using the selected retrieval mode."""
    if count() == 0:
        raise RuntimeError("Index is empty, call POST /knowledge/ask/index first")

    query_vectors, _ = knowledge.embed_texts([question], input_type="query")

    if SEARCH_MODE == "hybrid":
        return hybrid.search_with_vector(
            CHUNK_STRATEGY,
            question,
            query_vectors[0],
            top_k,
        )

    return chunk_index.search_with_vectors(CHUNK_STRATEGY,query_vectors,k=top_k,)[0]