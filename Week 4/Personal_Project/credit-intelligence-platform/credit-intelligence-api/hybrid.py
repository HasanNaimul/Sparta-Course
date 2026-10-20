"""Combine vector and BM25 retrieval using reciprocal rank fusion."""

import re
from functools import lru_cache

import bm25
import chunk_index
import chunking
import fusion

POOL = 10


@lru_cache(maxsize=None)
def keyword_index() -> bm25.BM25Index:
    return bm25.BM25Index(chunking.chunk_corpus())


def identifiers(text: str) -> set[str]:
    """Return structured identifiers such as FAC-2048 or COV-3102."""
    return set(re.findall(r"\b[a-z]+-\d+\b", text.lower()))


def search_with_vector(
    question: str,
    query_vector: list[float],
    top_k: int = 3,
    pool: int = POOL,
) -> list[dict]:
    vector_hits = chunk_index.search_with_vector(query_vector, top_k=pool)
    keyword_hits = keyword_index().search(question, top_k=pool)

    vector_ids = [hit["chunk_id"] for hit in vector_hits]
    keyword_ids = [hit["chunk"]["id"] for hit in keyword_hits]

    fused = fusion.reciprocal_rank_fusion([vector_ids, keyword_ids])

    vector_lookup = {hit["chunk_id"]: hit for hit in vector_hits}
    keyword_lookup = {hit["chunk"]["id"]: hit for hit in keyword_hits}

    wanted = identifiers(question)
    hits = []

    for chunk_id, rrf_score in fused[:top_k]:
        if chunk_id in vector_lookup:
            hit = dict(vector_lookup[chunk_id])
        else:
            chunk = keyword_lookup[chunk_id]["chunk"]
            hit = {
                "chunk_id": chunk["id"],
                "doc_id": chunk["doc_id"],
                "title": chunk["title"],
                "text": chunk["text"],
                "score": None,
            }

        found_by = []

        if chunk_id in vector_lookup:
            found_by.append("vector")

        if chunk_id in keyword_lookup:
            found_by.append("keyword")

        hit["found_by"] = found_by
        hit["exact_match"] = bool(wanted & identifiers(hit["text"]))
        hit["rrf"] = round(rrf_score, 5)

        hits.append(hit)

    return hits