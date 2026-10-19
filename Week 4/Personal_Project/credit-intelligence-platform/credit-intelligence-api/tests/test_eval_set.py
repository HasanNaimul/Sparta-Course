from credit_corpus import CREDIT_DOCUMENTS
from eval_set import EVAL_SET


def test_eval_set_has_enough_questions():
    assert len(EVAL_SET) >= 25


def test_question_ids_are_unique():
    ids = [q["id"] for q in EVAL_SET]
    assert len(ids) == len(set(ids))


def test_answerable_evidence_exists_in_labelled_document():
    docs = {doc["id"]: doc["body"] for doc in CREDIT_DOCUMENTS}
    for q in EVAL_SET:
        if q["doc_id"]:
            assert q["doc_id"] in docs
            assert q["evidence"] in docs[q["doc_id"]]


def test_answerable_questions_have_keywords():
    for q in EVAL_SET:
        if q["doc_id"]:
            assert q["keywords"]


def test_unanswerable_questions_have_no_evidence():
    for q in EVAL_SET:
        if not q["doc_id"]:
            assert q["evidence"] == ""
            assert q["keywords"] == []


def test_eval_set_covers_important_query_types():
    kinds = {q["kind"] for q in EVAL_SET}
    assert {"numeric", "exact-id", "negation", "policy", "unanswerable"} <= kinds