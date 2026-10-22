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

def test_credit_corpus_is_large_enough_for_retrieval_evaluation():
    assert len(CREDIT_DOCUMENTS) >= 20


def test_credit_corpus_contains_multiple_documents_for_same_borrower():
    northbridge = [doc for doc in CREDIT_DOCUMENTS if "Northbridge Components" in doc["title"]]
    assert len(northbridge) >= 3