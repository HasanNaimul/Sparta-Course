import embeddings


class FakeResponse:
    embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    total_tokens = 12


def test_embed_texts(monkeypatch):
    monkeypatch.setattr(embeddings.client, "embed", lambda texts, model, input_type: FakeResponse())

    vectors, tokens = embeddings.embed_texts(["first document", "second document"], input_type="document")

    assert len(vectors) == 2
    assert vectors[0] == [0.1, 0.2, 0.3]
    assert tokens == 12


def test_embed_empty_list():
    vectors, tokens = embeddings.embed_texts([], input_type="document")

    assert vectors == []
    assert tokens == 0