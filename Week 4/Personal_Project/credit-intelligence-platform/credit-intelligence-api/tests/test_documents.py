from data import BORROWERS
from documents import CREDIT_DOCUMENTS


def test_credit_document_count():
    assert len(CREDIT_DOCUMENTS) >= 8


def test_credit_document_ids_are_unique():
    ids = [doc["id"] for doc in CREDIT_DOCUMENTS]
    assert len(ids) == len(set(ids))


def test_credit_documents_have_required_fields():
    required = {"id", "borrower_id", "type", "date", "title", "body"}
    assert all(required <= doc.keys() for doc in CREDIT_DOCUMENTS)


def test_credit_document_borrower_ids_are_valid():
    borrower_ids = {borrower["id"] for borrower in BORROWERS}

    for doc in CREDIT_DOCUMENTS:
        assert doc["borrower_id"] is None or doc["borrower_id"] in borrower_ids