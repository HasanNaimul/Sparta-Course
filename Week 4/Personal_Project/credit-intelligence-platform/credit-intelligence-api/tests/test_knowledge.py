from types import SimpleNamespace

import knowledge


def test_embed_texts(monkeypatch):
    def fake_embed(texts, model, input_type):
        assert texts == ["credit risk", "covenant breach"]
        assert model == knowledge.EMBED_MODEL
        assert input_type == "document"
        return SimpleNamespace(embeddings=[[0.1, 0.2], [0.3, 0.4]], total_tokens=7)

    monkeypatch.setattr(knowledge.voyage, "embed", fake_embed)

    vectors, tokens = knowledge.embed_texts(["credit risk", "covenant breach"], "document")

    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    assert tokens == 7


def test_embed_empty_list_does_not_call_voyage(monkeypatch):
    def must_not_be_called(*args, **kwargs):
        raise AssertionError("Voyage should not be called")

    monkeypatch.setattr(knowledge.voyage, "embed", must_not_be_called)

    vectors, tokens = knowledge.embed_texts([], "document")

    assert vectors == []
    assert tokens == 0