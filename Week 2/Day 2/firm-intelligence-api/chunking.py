"""Chunking strategies.

Every strategy takes a document and returns a list of chunks.

A chunk is a dict:
    - id      "<doc id>#<two-digit-number>", stable for the same input
    - doc_id  the parent document, used for citations
    - title   the parent document's title
    - text    exactly what gets embedded and what the model will read
"""

import re


def _chunk(doc: dict, number: int, text: str) -> dict:
    return {
        "id": f"{doc['id']}#{number:02d}",
        "doc_id": doc["id"],
        "title": doc["title"],
        "text": text,
    }


def split_sentences(text: str) -> list[str]:
    """Split into sentences, keeping each '## Heading' line as its own unit."""
    units = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith("## "):
            units.append(line)
        else:
            units.extend(
                sentence
                for sentence in re.split(r"(?<=[.!?])\s+", line)
                if sentence
            )

    return units


def pack(units: list[str], max_words: int) -> list[str]:
    """Join whole units until adding the next one would pass max_words."""
    groups, current, count = [], [], 0

    for unit in units:
        n = len(unit.split())

        if current and count + n > max_words:
            groups.append(" ".join(current))
            current, count = [], 0

        current.append(unit)
        count += n

    if current:
        groups.append(" ".join(current))

    return groups


# ------------------------- CHUNKING STRATEGIES -------------------------


def whole_document(doc: dict) -> list[dict]:
    """Baseline: do not split the document."""
    return [_chunk(doc, 0, doc["body"].strip())]


def fixed_words(doc: dict, size: int = 100, overlap: int = 0) -> list[dict]:
    """Split every 'size' words, regardless of sentences or sections."""
    if not 0 <= overlap < size:
        raise ValueError("Overlap must be at least 0 and smaller than size")

    words = doc["body"].split()
    step = size - overlap
    chunks = []

    for number, start in enumerate(range(0, len(words), step)):
        text = " ".join(words[start:start + size])
        chunks.append(_chunk(doc, number, text))

        if start + size >= len(words):
            break

    return chunks


def sentenced_packed(doc: dict, max_words: int = 100) -> list[dict]:
    """Whole sentences only, packed up to max_words. Never cuts a sentence in half."""
    units = split_sentences(doc["body"])
    groups = pack(units, max_words)

    return [
        _chunk(doc, number, text)
        for number, text in enumerate(groups)
    ]


def by_section(doc: dict, max_words: int = 150, contextual: bool = True) -> list[dict]:
    """
    Split by '## ' section, then pack whole sentences up to max_words.

    If contextual=True, prefix each chunk with:
    "Document title > Section heading"

    This gives the embedding the document and section context even when
    the section text itself does not name its subject.
    """
    chunks, number = [], 0
    has_sections = "## " in doc["body"]

    parts = re.split(r"(?m)^## ", doc["body"]) if has_sections else [doc["body"]]

    for part in parts:
        if has_sections:
            heading, _, text = part.partition("\n")
        else:
            heading, text = "", part

        heading = heading.strip()
        text = text.strip()

        if not text:
            continue

        for piece in pack(split_sentences(text), max_words):
            if contextual:
                prefix = f"{doc['title']} > {heading}\n" if heading else f"{doc['title']}\n"
                piece = prefix + piece

            chunks.append(_chunk(doc, number, piece))
            number += 1

    return chunks


STRATEGIES = {
    "whole_document": whole_document,
    "fixed_100": lambda d: fixed_words(d, size=100, overlap=0),
    "fixed_100_overlap_25": lambda d: fixed_words(d, size=100, overlap=25),
    "sentences_100": lambda d: sentenced_packed(d, max_words=100),
    "sections_plain": lambda d: by_section(d, max_words=150, contextual=False),
    "sections_contextual": lambda d: by_section(d, max_words=150, contextual=True),
}


def chunk_corpus(docs: list[dict], strategy: str) -> list[dict]:
    """Apply one chunking strategy to every document and return one flat list."""
    return [
        chunk
        for doc in docs
        for chunk in STRATEGIES[strategy](doc)
    ]