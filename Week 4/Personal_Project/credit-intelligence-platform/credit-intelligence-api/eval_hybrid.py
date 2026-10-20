"""Evaluate hybrid retrieval against the labelled Credit Intelligence questions."""

from collections import defaultdict

import hybrid
import knowledge
from eval_set import EVAL_SET


def evaluate(top_k: int = 3) -> None:
    answerable = [q for q in EVAL_SET if q["doc_id"]]

    questions = [q["question"] for q in answerable]
    query_vectors, tokens = knowledge.embed_texts(questions, input_type="query")

    recall_at_1 = 0
    recall_at_3 = 0
    reciprocal_rank_total = 0.0
    by_kind = defaultdict(lambda: {"total": 0, "r1": 0, "r3": 0})
    misses = []

    for q, query_vector in zip(answerable, query_vectors):
        hits = hybrid.search_with_vector(q["question"], query_vector, top_k=top_k)

        doc_ids = [hit["doc_id"] for hit in hits]
        expected = q["doc_id"]

        rank = doc_ids.index(expected) + 1 if expected in doc_ids else None

        if rank == 1:
            recall_at_1 += 1

        if rank is not None and rank <= 3:
            recall_at_3 += 1

        if rank:
            reciprocal_rank_total += 1 / rank
        else:
            misses.append(q["id"])

        kind = by_kind[q["kind"]]
        kind["total"] += 1

        if rank == 1:
            kind["r1"] += 1

        if rank is not None and rank <= 3:
            kind["r3"] += 1

        top_doc = doc_ids[0] if doc_ids else None
        print(f'{q["id"]}: expected={expected} rank={rank} top={top_doc}')

    total = len(answerable)

    print("\nOverall")
    print(f"Questions: {total}")
    print(f"Embedding tokens: {tokens}")
    print(f"Recall@1: {recall_at_1 / total:.3f}")
    print(f"Recall@3: {recall_at_3 / total:.3f}")
    print(f"MRR:      {reciprocal_rank_total / total:.3f}")
    print(f"Misses:   {misses or 'none'}")

    print("\nBy kind")

    for kind, values in sorted(by_kind.items()):
        total_kind = values["total"]

        print(
            f"{kind:12} "
            f"R@1={values['r1'] / total_kind:.3f} "
            f"R@3={values['r3'] / total_kind:.3f}"
        )


if __name__ == "__main__":
    evaluate()