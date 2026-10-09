"""A chunker must not lose, duplicate or mangle text."""

import pytest

import chunking
from corpus import CORPUS_DOCUMENTS
from routers.documents import DOCUMENTS


DOC = next(d for d in CORPUS_DOCUMENTS if d["id"] == "doc-105")
ALL_DOCS = DOCUMENTS + CORPUS_DOCUMENTS


def test_fixed_chunks_without_overlap_lose_no_words():
    chunks = chunking.fixed_words(DOC, size=100, overlap=0)
    rebuilt = " ".join(c["text"] for c in chunks).split()

    assert rebuilt == DOC["body"].split()
    # if the chunker is correct, we get back the same words in the same order


def test_overlap_repeats_exactly_the_overlap_words():
    chunks = chunking.fixed_words(DOC, size=100, overlap=25)

    for first, second in zip(chunks, chunks[1:]):
        assert first["text"].split()[-25:] == second["text"].split()[:25]


# test overlap must be smaller than size
def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunking.fixed_words(DOC, size=100, overlap=100)


# test sentence packing never cuts a sentence
def test_sentence_packing_never_cuts_a_sentence():
    chunks = chunking.sentenced_packed(DOC, max_words=100)
    sentences = chunking.split_sentences(DOC["body"])

    for sentence in sentences:
        assert any(sentence in chunk["text"] for chunk in chunks)


# test contextual sections carry title and heading
def test_contextual_sections_carry_title_and_heading():
    chunks = chunking.by_section(DOC, max_words=150, contextual=True)

    tokyo_chunk = next(
        c for c in chunks
        if "It employs 38 lawyers" in c["text"]
    )

    assert DOC["title"] in tokyo_chunk["text"]
    assert "Tokyo" in tokyo_chunk["text"]


# test plain sections carry no title or heading prefix
def test_plain_sections_carry_no_heading():
    chunks = chunking.by_section(DOC, max_words=150, contextual=False)

    tokyo_chunk = next(
        c for c in chunks
        if "It employs 38 lawyers" in c["text"]
    )

    assert not tokyo_chunk["text"].startswith(DOC["title"])
    assert not tokyo_chunk["text"].startswith("Tokyo")