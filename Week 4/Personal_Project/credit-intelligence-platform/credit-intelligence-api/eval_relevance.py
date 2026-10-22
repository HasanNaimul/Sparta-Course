"""Evaluate relevance floors for the final Credit Intelligence hybrid retriever."""

import time

import voyageai

import hybrid
import knowledge
from eval_set import EVAL_SET

STRATEGY = "title_contextual_100"
BATCH_SIZE = 20
BATCH_PAUSE = 22
RETRY_SECONDS = 25

FLOORS = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]


def embed_queries(questions: list[str]) -> tuple[list[list[float]], int]:
    vectors, total_tokens = [], 0

    for start in range(0, len(questions), BATCH_SIZE):
        batch = questions[start:start + BATCH_SIZE]

        while True:
            try:
                batch_vectors, tokens = knowledge.embed_texts(batch, input_type="query")
                vectors.extend(batch_vectors)
                total_tokens += tokens
                break
            except voyageai.error.RateLimitError:
                print(f"Voyage rate limit reached. Retrying in {RETRY_SECONDS} seconds...")
                time.sleep(RETRY_SECONDS)

        if start + BATCH_SIZE < len(questions):
            time.sleep(BATCH_PAUSE)

    return vectors, total_tokens


def is_usable(hit: dict, floor: float, exact_bypass: bool) -> bool:
    if exact_bypass and hit.get("exact_match", False):
        return True

    score = hit.get("score")
    return score is not None and score >= floor


def evaluate_mode(results: list[dict], exact_bypass: bool) -> None:
    answerable_total = sum(q["doc_id"] is not None for q in EVAL_SET)
    unanswerable_total = sum(q["doc_id"] is None for q in EVAL_SET)

    print("\n" + "=" * 90)
    print(f"EXACT-MATCH BYPASS: {'ON' if exact_bypass else 'OFF'}")
    print("=" * 90)

    for floor in FLOORS:
        accepted_answerable = 0
        refused_unanswerable = 0
        false_refusals = []
        false_accepts = []

        for result in results:
            q = result["question"]
            usable = [hit for hit in result["hits"] if is_usable(hit, floor, exact_bypass)]
            accepted = bool(usable)

            if q["doc_id"]:
                if accepted:
                    accepted_answerable += 1
                else:
                    false_refusals.append(q["id"])
            else:
                if accepted:
                    false_accepts.append(q["id"])
                else:
                    refused_unanswerable += 1

        print(
            f"floor={floor:.2f} "
            f"answerable={accepted_answerable}/{answerable_total} "
            f"unanswerable_refused={refused_unanswerable}/{unanswerable_total} "
            f"false_refusals={false_refusals or 'none'} "
            f"false_accepts={false_accepts or 'none'}"
        )


def evaluate() -> None:
    questions = [q["question"] for q in EVAL_SET]
    query_vectors, tokens = embed_queries(questions)
    results = []

    for q, vector in zip(EVAL_SET, query_vectors):
        hits = hybrid.search_with_vector(q["question"], vector, top_k=5, strategy=STRATEGY)
        top = hits[0]

        score = top.get("score")
        score_text = f"{score:.3f}" if score is not None else "None"

        results.append({"question": q, "hits": hits})

        print(
            f'{q["id"]}: '
            f'answerable={q["doc_id"] is not None} '
            f'top={top["doc_id"]} '
            f'score={score_text} '
            f'exact={top["exact_match"]}'
        )

    print(f"\nEmbedding tokens: {tokens}")

    evaluate_mode(results, exact_bypass=True)
    evaluate_mode(results, exact_bypass=False)


if __name__ == "__main__":
    evaluate()