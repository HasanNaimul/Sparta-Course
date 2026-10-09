"""One Chroma collection per chunking strategy so strategies can be compared side by side.

Each collection remembers a fingerprint of the chunks and embedding model that built it.
If either changes, the collection is rebuilt from scratch.
"""

import hashlib
import chromadb
import chunking
from corpus import CORPUS_DOCUMENTS
from routers.documents import DOCUMENTS
from routers import knowledge_store as knowledge

ALL_DOCUMENTS = DOCUMENTS + CORPUS_DOCUMENTS
BATCH_SIZE = 128

chroma = chromadb.PersistentClient(path="./chroma_store")


def collection_name(strategy: str) -> str:
    return f"chunks_{strategy}"


def collection_for(strategy: str):
    return chroma.get_or_create_collection(name=collection_name(strategy), configuration={"hnsw": {"space": "cosine"}})


def embed_batched(texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    """Embed texts in batches and return all vectors plus total token count."""
    vectors: list[list[float]] = []
    tokens = 0

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        batch_vectors, batch_tokens = knowledge.embed_texts(batch, input_type=input_type)
        vectors.extend(batch_vectors)
        tokens += batch_tokens

    return vectors, tokens


def fingerprint(chunks: list[dict]) -> str:
    """Fingerprint changes if the model, chunk ids, text or order changes."""
    digest = hashlib.sha256(knowledge.EMBED_MODEL.encode())

    for chunk in chunks:
        digest.update(f"{chunk['id']}\n{chunk['text']}\n".encode())

    return digest.hexdigest()[:16]


def build(strategy: str, force: bool = False) -> dict:
    """Reuse the collection if it still matches, otherwise rebuild it."""
    if strategy not in chunking.STRATEGIES:
        raise ValueError(f"Unknown chunking strategy: {strategy}")

    chunks = chunking.chunk_corpus(ALL_DOCUMENTS, strategy)
    fp = fingerprint(chunks)
    col = collection_for(strategy)
    stored = col.get(limit=1, include=["metadatas"])["metadatas"]

    if not force and col.count() == len(chunks) and stored and stored[0].get("fingerprint") == fp:
        return {"strategy": strategy, "chunks": len(chunks), "embedding_tokens": 0, "rebuilt": False, "fingerprint": fp}

    try:
        chroma.delete_collection(collection_name(strategy))
    except Exception:
        pass

    col = collection_for(strategy)
    vectors, tokens = embed_batched([chunk["text"] for chunk in chunks], input_type="document")

    col.upsert(
        ids=[chunk["id"] for chunk in chunks],
        embeddings=vectors,
        documents=[chunk["text"] for chunk in chunks],
        metadatas=[{"doc_id": chunk["doc_id"], "title": chunk["title"], "fingerprint": fp} for chunk in chunks],
    )

    return {"strategy": strategy, "chunks": len(chunks), "embedding_tokens": tokens, "rebuilt": True}