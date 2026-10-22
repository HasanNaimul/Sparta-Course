"""Evaluate final hybrid retrieval against the expanded Credit Intelligence eval set."""

import time

import voyageai

import hybrid
import knowledge
from eval_set import EVAL_SET

STRATEGY = "title_contextual_100"
BATCH_SIZE = 20
BATCH_PAUSE = 22
RETRY_SECONDS = 25


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


def evaluate() -> None:
    answerable = [q for q in EVAL_SET if q["doc_id"]]
    query_vectors, tokens = embed_queries([q["question"] for q in answerable])

    r1 = r3 = r5 = 0
    mrr = 0.0
    exact_total = exact_r1 = 0
    misses = []
    wrong_top = []

    for q, vector in zip(answerable, query_vectors):
        hits = hybrid.search_with_vector(q["question"], vector, top_k=5, strategy=STRATEGY)
        doc_ids = [hit["doc_id"] for hit in hits]

        expected = q["doc_id"]
        rank = doc_ids.index(expected) + 1 if expected in doc_ids else None

        r1 += rank == 1
        r3 += rank is not None and rank <= 3
        r5 += rank is not None and rank <= 5

        if rank:
            mrr += 1 / rank
        else:
            misses.append(q["id"])

        if rank != 1:
            wrong_top.append((q["id"], rank, doc_ids[0] if doc_ids else None))

        if q["kind"] == "exact-id":
            exact_total += 1
            exact_r1 += rank == 1

        print(f'{q["id"]}: expected={expected} rank={rank} top={doc_ids[0] if doc_ids else None}')

    total = len(answerable)

    print("\nResults")
    print(f"Questions:       {total}")
    print(f"Embedding tokens:{tokens}")
    print(f"Recall@1:        {r1 / total:.3f}")
    print(f"Recall@3:        {r3 / total:.3f}")
    print(f"Recall@5:        {r5 / total:.3f}")
    print(f"MRR:             {mrr / total:.3f}")
    print(f"Exact-ID R@1:    {exact_r1 / exact_total:.3f}")
    print(f"Misses:          {misses or 'none'}")
    print(f"Wrong top hits:  {wrong_top or 'none'}")


if __name__ == "__main__":
    evaluate()