"""Chunking strategies for Credit Intelligence retrieval experiments."""

import re

from credit_corpus import CREDIT_DOCUMENTS

STRATEGIES = [
    "whole_document",
    "fixed_100",
    "fixed_100_overlap_25",
    "sentences_100",
    "title_contextual_100",
]


def _fixed_chunks(text: str, size: int = 100, overlap: int = 0) -> list[str]:
    words = text.split()
    step = size - overlap
    return [" ".join(words[start:start + size]) for start in range(0, len(words), step) if words[start:start + size]]


def _sentence_chunks(text: str, size: int = 100) -> list[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    chunks, current, current_words = [], [], 0

    for sentence in sentences:
        words = sentence.split()

        if current and current_words + len(words) > size:
            chunks.append(" ".join(current))
            current, current_words = [], 0

        if len(words) > size:
            chunks.extend(_fixed_chunks(sentence, size))
        else:
            current.append(sentence)
            current_words += len(words)

    if current:
        chunks.append(" ".join(current))

    return chunks


def _texts_for(doc: dict, strategy: str) -> list[str]:
    if strategy == "whole_document":
        return [f'{doc["title"]}\n\n{doc["body"]}']

    if strategy == "fixed_100":
        return _fixed_chunks(doc["body"], 100)

    if strategy == "fixed_100_overlap_25":
        return _fixed_chunks(doc["body"], 100, 25)

    if strategy == "sentences_100":
        return _sentence_chunks(doc["body"], 100)

    if strategy == "title_contextual_100":
        return [f'{doc["title"]}\n{doc["type"]}\n\n{text}' for text in _fixed_chunks(doc["body"], 100)]

    raise ValueError(f"Unknown chunking strategy: {strategy}")


def chunk_corpus(strategy: str = "whole_document") -> list[dict]:
    chunks = []

    for doc in CREDIT_DOCUMENTS:
        for index, text in enumerate(_texts_for(doc, strategy)):
            chunks.append({
                "id": f'{doc["id"]}#{index:02d}',
                "doc_id": doc["id"],
                "title": doc["title"],
                "type": doc["type"],
                "text": text,
            })

    return chunks