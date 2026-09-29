

# Embedded texts are imported, not rewritten.
# The embedding provider has not changed, only where the vectors get stored.

import chromadb

from routers.documents import DOCUMENTS
from knowledge import embed_texts


# PersistentClient means the vectors are stored on disk
chroma = chromadb.PersistentClient(
    path="./chroma_store"
)


# Get the collection if it exists, otherwise create it
collection = chroma.get_or_create_collection(
    name="firm_documents",
    # HNSW (hierachchial Navigable Small World) is a graph based index used in vector database to perform fast and appropriate nearest neighbour search in high dimensional data
    configuration={
        "hnsw": {
            "space": "cosine"
        }
    },
)

def build_index() -> int:
    """Embed every document and store the vectors in ChromaDB."""

    texts = [doc["body"] for doc in DOCUMENTS]

    vectors, tokens = embed_texts(
        texts,
        input_type="document"
    )

    collection.upsert(
        ids=[doc["id"] for doc in DOCUMENTS],
        embeddings=vectors,
        documents=texts,
        metadatas=[
            {
                "title": doc["title"],
                "type": doc["type"],
            }
            for doc in DOCUMENTS
        ],
    )

    return tokens

# Chroma gives us distance: lower = closer
# For cosine distance, score = 1 - distance

def search(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question and let Chroma do the searching."""

    query_vectors, _ = embed_texts(
        [question],
        input_type="query"
    )

    result = collection.query(
        query_embeddings=query_vectors,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    return [
        {
            "id": doc_id,
            "title": metadata["title"],
            "text": text,
            "score": 1 - distance,
        }
        for doc_id, metadata, text, distance in zip(
            result["ids"][0],
            result["metadatas"][0],
            result["documents"][0],
            result["distances"][0],
        )
    ]


# Things to note from our switch to ChromaDB

# 1. embed_texts() is imported, not rewritten.
#    The embedding provider has not changed.
#    We still use Voyage AI to create the vectors.
#    Only the place where those vectors are stored/searchable has changed.

# 2. configuration=... is deliberate.
#    We configure Chroma to use cosine distance because our previous
#    retrieval logic was based on cosine similarity.

# 3. Chroma returns distance, while our old code returned similarity.
#    In Chroma:
#        lower distance = closer / more similar
#
#    In our old system:
#        higher similarity score = closer / more similar
#
#    We convert:
#        similarity = 1 - distance

# 4. We use upsert() instead of add().
#    add() is for inserting new IDs and can fail if the ID already exists.
#    upsert() means:
#        insert if the ID is new
#        update/overwrite if the ID already exists
#
#    This makes rebuilding the index safer.