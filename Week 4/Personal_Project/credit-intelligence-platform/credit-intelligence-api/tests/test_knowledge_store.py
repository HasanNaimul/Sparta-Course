import knowledge_store


def test_count_uses_chunk_index(monkeypatch):
    monkeypatch.setattr(knowledge_store.chunk_index, "count", lambda strategy: 10)
    assert knowledge_store.count() == 10


def test_search_refuses_empty_index(monkeypatch):
    monkeypatch.setattr(knowledge_store, "count", lambda: 0)

    try:
        knowledge_store.search("What is FAC-2048?")
        assert False
    except RuntimeError as error:
        assert "empty" in str(error).lower()


def test_hybrid_search(monkeypatch):
    monkeypatch.setattr(knowledge_store, "count", lambda: 10)
    monkeypatch.setattr(knowledge_store.knowledge, "embed_texts", lambda texts, input_type: ([[0.1, 0.2]], 3))
    monkeypatch.setattr(
        knowledge_store.hybrid,
        "search_with_vector",
        lambda question, vector, top_k, strategy=None: [{"doc_id": "credit-doc-001"}],
    )

    hits = knowledge_store.search("What is FAC-2048?")

    assert hits[0]["doc_id"] == "credit-doc-001"