"""Persistent Chroma vector index for Credit Intelligence."""

import chromadb

import chunking
import knowledge

CHROMA_PATH = "./chroma_store"
COLLECTION = "credit_intelligence"


def collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def build() -> int:
    chunks = chunking.chunk_corpus()
    texts = [chunk["text"] for chunk in chunks]

    vectors, tokens = knowledge.embed_texts(texts, input_type="document")

    collection().upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=texts,
        embeddings=vectors,
        metadatas=[
            {
                "doc_id": chunk["doc_id"],
                "title": chunk["title"],
            }
            for chunk in chunks
        ],
    )

    return tokens


def count() -> int:
    return collection().count()


def search_with_vector(query_vector: list[float], top_k: int = 3) -> list[dict]:
    results = collection().query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []

    for chunk_id, text, metadata, distance in zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "chunk_id": chunk_id,
            "doc_id": metadata["doc_id"],
            "title": metadata["title"],
            "text": text,
            "score": 1 - distance,
        })

    return hits


def search(question: str, top_k: int = 3) -> list[dict]:
    vectors, _ = knowledge.embed_texts([question], input_type="query")
    return search_with_vector(vectors[0], top_k)