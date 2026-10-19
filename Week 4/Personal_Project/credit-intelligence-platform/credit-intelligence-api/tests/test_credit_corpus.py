from credit_corpus import CREDIT_DOCUMENTS


def test_credit_corpus_has_at_least_eight_documents():
    assert len(CREDIT_DOCUMENTS) >= 8


def test_credit_document_ids_are_unique():
    ids = [doc["id"] for doc in CREDIT_DOCUMENTS]
    assert len(ids) == len(set(ids))


def test_credit_documents_have_required_fields():
    for doc in CREDIT_DOCUMENTS:
        assert doc["id"]
        assert doc["title"]
        assert doc["type"]
        assert doc["body"]