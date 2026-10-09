import re

from corpus import CORPUS_DOCUMENTS
from routers.documents import DOCUMENTS
from eval_set import EVAL_SET, answerable
from eval_tools import contains_evidence, keywords_present
from grounding import normalise


ALL_DOCS = {d["id"]: d for d in DOCUMENTS + CORPUS_DOCUMENTS}

def section_containing(body: str, evidence: str) -> tuple[str, str]:
    """Return (heading, section text) for the section holding the evidence."""
    for part in re.split(r"(?m)^## ", body):
        heading, _, text = part.partition("\n")
        if contains_evidence(text, evidence):
            return heading.strip(), text
    raise AssertionError(f"evidence not found in any section: {evidence}")

# test ids are unique
def test_ids_are_unique():
    ids = [q["id"] for q in EVAL_SET]

    assert len(ids) == len(set(ids))


# test every evidence span is in its document
def test_every_evidence_span_is_in_its_document():
    for q in answerable():
        doc = ALL_DOCS[q["doc_id"]]

        assert contains_evidence(doc["body"], q["evidence"]), (f"{q['id']} evidence not found in {q['doc_id']}")

# test every evidence span appears exactly once in the whole corpus
def test_every_evidence_span_appears_exactly_once():
    whole_corpus = "\n".join(doc["body"] for doc in ALL_DOCS.values())
    normalised_corpus = normalise(whole_corpus)

    for q in answerable():
        evidence = normalise(q["evidence"])
        count = normalised_corpus.count(evidence)

        assert count == 1, (f"{q['id']} evidence appears {count} times instead of once")

# test keyword matching is whole-word and refusal-aware
def test_keyword_matching_is_whole_word_and_refusal_aware():
    assert keywords_present("There are no outstanding regulatory matters.", ["no"]) is True

    # "no" must not match inside a bigger word such as "notable"
    assert keywords_present("The result was notable.", ["no"]) is False

    # A refusal must never count as a correct answer, even if it contains a keyword
    assert keywords_present("The provided documents do not answer that question.",["documents"],) is False