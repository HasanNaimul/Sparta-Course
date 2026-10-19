"""Turn credit documents into retrieval-ready chunks."""

from credit_corpus import CREDIT_DOCUMENTS


def chunk_corpus() -> list[dict]:
    chunks = []

    for doc in CREDIT_DOCUMENTS:
        chunks.append({
            "id": f'{doc["id"]}#00',
            "doc_id": doc["id"],
            "title": doc["title"],
            "text": f'{doc["title"]}\n\n{doc["body"]}',
        })

    return chunks