import chunking


def test_chunk_corpus_has_chunks():
    assert len(chunking.chunk_corpus()) > 0


def test_chunks_have_required_fields():
    for chunk in chunking.chunk_corpus():
        assert chunk["id"]
        assert chunk["doc_id"]
        assert chunk["title"]
        assert chunk["text"]


def test_chunk_ids_are_unique():
    chunks = chunking.chunk_corpus()
    ids = [chunk["id"] for chunk in chunks]
    assert len(ids) == len(set(ids))