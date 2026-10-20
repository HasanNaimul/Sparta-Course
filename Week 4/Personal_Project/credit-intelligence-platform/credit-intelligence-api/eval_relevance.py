"""Inspect retrieval scores and test candidate relevance floors."""

import hybrid
import knowledge
from eval_set import EVAL_SET


FLOORS = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]


def is_usable(hit: dict, floor: float) -> bool:
    return hit.get("exact_match", False) or hit["score"] >= floor


def evaluate() -> None:
    questions = [q["question"] for q in EVAL_SET]
    query_vectors, tokens = knowledge.embed_texts(questions, input_type="query")

    results = []

    for q, query_vector in zip(EVAL_SET, query_vectors):
        hits = hybrid.search_with_vector(q["question"], query_vector, top_k=3)
        top = hits[0]

        results.append({
            "id": q["id"],
            "answerable": q["doc_id"] is not None,
            "doc_id": top["doc_id"],
            "score": top["score"],
            "exact_match": top["exact_match"],
            "hits": hits,
        })

        print(
            f'{q["id"]}: '
            f'answerable={q["doc_id"] is not None} '
            f'top={top["doc_id"]} '
            f'score={top["score"]:.3f} '
            f'exact={top["exact_match"]}'
        )

    print(f"\nEmbedding tokens: {tokens}")

    print("\nCandidate floors")

    for floor in FLOORS:
        accepted_answerable = 0
        refused_answerable = []
        refused_unanswerable = 0
        accepted_unanswerable = []

        for q, result in zip(EVAL_SET, results):
            usable = [hit for hit in result["hits"] if is_usable(hit, floor)]
            accepted = bool(usable)

            if q["doc_id"]:
                if accepted:
                    accepted_answerable += 1
                else:
                    refused_answerable.append(q["id"])
            else:
                if accepted:
                    accepted_unanswerable.append(q["id"])
                else:
                    refused_unanswerable += 1

        answerable_total = sum(q["doc_id"] is not None for q in EVAL_SET)
        unanswerable_total = sum(q["doc_id"] is None for q in EVAL_SET)

        print(
            f"floor={floor:.2f} "
            f"answerable={accepted_answerable}/{answerable_total} "
            f"unanswerable_refused={refused_unanswerable}/{unanswerable_total} "
            f"false_refusals={refused_answerable or 'none'} "
            f"false_accepts={accepted_unanswerable or 'none'}"
        )


if __name__ == "__main__":
    evaluate()