"""Hybrid search: vector search and keyword search, merged by rank."""

from functools import lru_cache

import bm25
import chunk_index
import chunking
import fusion

POOL = 10


# Helper 1: build the BM25 index once per chunking strategy.
@lru_cache(maxsize=None)
def keyword_index(strategy: str) -> bm25.BM25Index:
    """Build and cache BM25 over the same chunks as the vector index."""
    chunks = chunking.chunk_corpus(chunk_index.ALL_DOCUMENTS, strategy)
    return bm25.BM25Index(chunks)


# Helper 2: find identifier-like tokens containing numbers.
def identifiers(text: str) -> set[str]:
    """Return tokens containing digits, for example 3307 from LP-3307."""
    return {
        token
        for token in bm25.tokenize(text)
        if any(ch.isdigit() for ch in token)
    }


# Helper 3: relevance gate.
def is_usable(hit: dict, floor: float) -> bool:
    """Pass if cosine clears the floor or there is an exact identifier match."""
    return hit["score"] >= floor or hit.get("exact_match", False)


def search_with_vector(
    strategy: str,
    question: str,
    query_vector: list[float],
    top_k: int = 3,
    pool: int = POOL,
) -> list[dict]:
    """Return top chunks found by vector search, keyword search, or both."""

    # Ask both retrievers for a larger candidate pool.
    vector_hits = chunk_index.search_with_vectors(
        strategy,
        [query_vector],
        k=pool,
    )[0]

    keyword_hits = keyword_index(strategy).search(
        question,
        k=pool,
    )

    # RRF only needs ranked IDs, not the original scores.
    fused = fusion.reciprocal_rank_fusion([
        [hit["chunk_id"] for hit in vector_hits],
        [hit["chunk"]["id"] for hit in keyword_hits],
    ])[:top_k]

    # Lookup tables so we can quickly find each result by chunk ID.
    by_vector = {
        hit["chunk_id"]: hit
        for hit in vector_hits
    }

    by_keyword = {
        hit["chunk"]["id"]: hit["chunk"]
        for hit in keyword_hits
    }

    # BM25 may find chunks that were not in the vector top results.
    # Those chunks still need a cosine score for our relevance gate.
    keyword_only = [
        chunk_id
        for chunk_id in by_keyword
        if chunk_id not in by_vector
    ]

    extra_cosine = chunk_index.cosine_for(
        strategy,
        query_vector,
        keyword_only,
    )

    # If BM25 knows about a chunk but Chroma does not, the two indexes
    # are out of sync and should be rebuilt.
    unknown = [
        chunk_id
        for chunk_id in keyword_only
        if chunk_id not in extra_cosine
    ]

    if unknown:
        raise RuntimeError(
            f"{unknown[0]} is in the keyword index but not in the vector index. "
            "Rebuild with POST /knowledge/index"
        )

    # Find identifier-like terms in the question, e.g. 3307.
    wanted = identifiers(question)

    # Build the final standard hit objects.
    hits = []

    for chunk_id, rrf_score in fused:
        if chunk_id in by_vector:
            hit = dict(by_vector[chunk_id])
        else:
            chunk = by_keyword[chunk_id]

            hit = {
                "id": chunk["doc_id"],
                "chunk_id": chunk_id,
                "title": chunk["title"],
                "text": chunk["text"],
                "score": extra_cosine[chunk_id],
            }

        # Record which retriever found the chunk.
        hit["found_by"] = [
            name
            for name, found in (
                ("vector", chunk_id in by_vector),
                ("keyword", chunk_id in by_keyword),
            )
            if found
        ]

        # Allow an exact identifier match to pass the relevance gate even
        # when semantic cosine similarity is weak.
        hit["exact_match"] = bool(
            wanted & set(bm25.tokenize(hit["text"]))
        )

        # Keep the RRF score separate from cosine similarity.
        hit["rrf"] = round(rrf_score, 5)

        hits.append(hit)

    return hits