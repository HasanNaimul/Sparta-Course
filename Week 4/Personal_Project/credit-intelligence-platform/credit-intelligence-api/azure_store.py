"""Azure AI Search backend for Credit Intelligence."""

import time
from functools import lru_cache

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery

import azure_index
import chunk_index
import hybrid
from config import settings

CANDIDATES = 50
BATCH = 100
NOT_BUILT = "The Azure index is empty or missing. Build it with: python -m azure_build"


@lru_cache(maxsize=None)
def _credential() -> DefaultAzureCredential:
    return DefaultAzureCredential()


def _endpoint() -> str:
    if not settings.azure_search_endpoint:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT is not set.")
    return settings.azure_search_endpoint


@lru_cache(maxsize=None)
def search_client() -> SearchClient:
    return SearchClient(endpoint=_endpoint(), index_name=settings.azure_search_index, credential=_credential())


@lru_cache(maxsize=None)
def index_client() -> SearchIndexClient:
    return SearchIndexClient(endpoint=_endpoint(), credential=_credential())


def count() -> int:
    try:
        return search_client().search(search_text="*", include_total_count=True, top=0).get_count() or 0
    except ResourceNotFoundError:
        return 0


def search_with_vector(question: str, query_vector: list[float], top_k: int = 5, semantic: bool = True) -> list[dict]:
    search_text = " ".join(question.split()) or "*"

    options = {
        "search_text": search_text,
        "vector_queries": [VectorizedQuery(vector=query_vector, k_nearest_neighbors=CANDIDATES, fields="embedding")],
        "select": ["chunk_id", "doc_id", "title", "text"],
        "top": CANDIDATES,
    }

    if semantic:
        options["query_type"] = "semantic"
        options["semantic_configuration_name"] = settings.semantic_config

    try:
        results = list(search_client().search(**options))[:top_k]
    except ResourceNotFoundError as error:
        raise RuntimeError(NOT_BUILT) from error

    if not results:
        raise RuntimeError(NOT_BUILT)

    wanted = hybrid.identifiers(question) if settings.exact_match_rule else set()
    hits = []

    for result in results:
        reranker_score = result.get("@search.reranker_score")
        fused_score = result["@search.score"]
        text = result["text"]

        hits.append({
            "chunk_id": result["chunk_id"],
            "doc_id": result["doc_id"],
            "title": result["title"],
            "text": text,
            "score": reranker_score if reranker_score is not None else fused_score,
            "reranker_score": reranker_score,
            "rrf": round(fused_score, 5),
            "exact_match": bool(wanted & hybrid.identifiers(text)),
        })

    return hits


def _local_chunks(strategy: str) -> list[dict]:
    """Reuse the existing Voyage vectors already stored locally."""
    chunk_index.build(strategy)
    stored = chunk_index.collection(strategy).get(include=["embeddings", "documents", "metadatas"])

    return [
        {
            "chunk_key": azure_index.key_for(chunk_id),
            "chunk_id": chunk_id,
            "doc_id": metadata["doc_id"],
            "title": metadata["title"],
            "text": text,
            "embedding": [float(number) for number in vector],
        }
        for chunk_id, vector, text, metadata in zip(stored["ids"], stored["embeddings"], stored["documents"], stored["metadatas"])
    ]


def _wait_until_counted(expected: int, seconds: int = 30) -> None:
    deadline = time.time() + seconds

    while time.time() < deadline:
        if count() >= expected:
            return
        time.sleep(1)

    raise RuntimeError(f"Uploaded {expected} chunks, but Azure reports {count()} after {seconds} seconds")


def build_index(strategy: str) -> int:
    docs = _local_chunks(strategy)
    keys = [doc["chunk_key"] for doc in docs]

    if len(set(keys)) != len(keys):
        raise RuntimeError("Two chunk ids produce the same Azure key")

    bad = [doc for doc in docs if len(doc["embedding"]) != azure_index.DIMENSIONS]
    if bad:
        raise RuntimeError(f"{bad[0]['chunk_id']} has {len(bad[0]['embedding'])} vector dimensions; expected {azure_index.DIMENSIONS}")

    name = settings.azure_search_index

    try:
        index_client().delete_index(name)
    except ResourceNotFoundError:
        pass

    index_client().create_index(azure_index.index_definition(name))

    for start in range(0, len(docs), BATCH):
        results = search_client().upload_documents(documents=docs[start:start + BATCH])
        failed = [result for result in results if not result.succeeded]

        if failed:
            raise RuntimeError(f"Azure rejected {len(failed)} chunks. First: {failed[0].key}: {failed[0].error_message}")

    _wait_until_counted(len(docs))
    return len(docs)