"""Azure AI Search backend - this does the same job as knowledge_store.

One search call does 3 things:
1. keyword search (BM25) and vector search run together, and Azure fuses them with RRF
2. the semantic reranker rereads the top results beside the question and scores each 0 to 4
3. the hits come back best first, carrying that score for the relevance gate (gate.py)
"""

from functools import lru_cache

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

import bm25
import settings

CANDIDATES = 50
BATCH = 100

NOT_BUILT = "The Azure index is empty or missing. Build it with: python -m azure_build"


@lru_cache(maxsize=None)
def _credential() -> DefaultAzureCredential:
    """Signs in as you after 'az login', or as the managed identity once deployed."""
    return DefaultAzureCredential()


def _endpoint() -> str:
    if not settings.AZURE_SEARCH_ENDPOINT:
        raise RuntimeError(
            "AZURE_SEARCH_ENDPOINT is not set. "
            "Example: export AZURE_SEARCH_ENDPOINT=https://<your-service>.search.windows.net"
        )
    return settings.AZURE_SEARCH_ENDPOINT


@lru_cache(maxsize=None)
def search_client() -> SearchClient:
    return SearchClient(
        endpoint=_endpoint(),
        index_name=settings.AZURE_SEARCH_INDEX,
        credential=_credential(),
    )


@lru_cache(maxsize=None)
def index_client() -> SearchIndexClient:
    return SearchIndexClient(endpoint=_endpoint(), credential=_credential())


def _identifiers(text: str) -> set[str]:
    """Tokens containing a digit (e.g. 3307), same as in hybrid.py."""
    return {token for token in bm25.tokenize(text) if any(ch.isdigit() for ch in token)}


def count() -> int:
    """Number of chunks in the Azure index, or 0 if it does not exist."""
    try:
        return search_client().search(search_text="*", include_total_count=True, top=0).get_count() or 0
    except ResourceNotFoundError:
        return 0


def search_with_vector(question: str, query_vector: list[float], top_k: int = 3, semantic: bool = True) -> list[dict]:
    clean_question = " ".join(bm25.tokenize(question))

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=CANDIDATES,
        fields="embedding",
    )

    search_args = {
        "search_text": clean_question,
        "vector_queries": [vector_query],
        "top": CANDIDATES,
        "select": ["chunk_id", "doc_id", "title", "text"],
    }

    if semantic:
        search_args["query_type"] = "semantic"
        search_args["semantic_configuration_name"] = settings.SEMANTIC_CONFIG

    try:
        results = list(search_client().search(**search_args))
    except ResourceNotFoundError:
        raise RuntimeError(NOT_BUILT)

    wanted = _identifiers(question)
    hits = []

    for result in results[:top_k]:
        text = result["text"]

        hits.append({
            "chunk_id": result["chunk_id"],
            "doc_id": result["doc_id"],
            "title": result["title"],
            "text": text,
            "score": result.get("@search.score"),
            "reranker_score": result.get("@search.reranker_score"),
            "exact_match": bool(wanted & _identifiers(text)),
        })

    return hits