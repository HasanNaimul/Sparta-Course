"""Evaluate Azure AI Search retrieval and semantic relevance gating."""

import time

import voyageai

import azure_store
import knowledge
from eval_set import EVAL_SET

TOP_K = 5
BATCH_SIZE = 20
BATCH_PAUSE = 22
RETRY_SECONDS = 25
RERANK_FLOORS = [1.0, 1.5, 2.0, 2.5, 3.0]


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
    vectors, tokens = embed_queries([q["question"] for q in EVAL_SET])
    results = []

    r1 = r3 = r5 = exact_total = exact_r1 = 0
    mrr = 0.0
    misses = []

    for q, vector in zip(EVAL_SET, vectors):
        hits = azure_store.search_with_vector(q["question"], vector, top_k=TOP_K)
        results.append({"question": q, "hits": hits})

        expected = q["doc_id"]

        if expected:
            doc_ids = [hit["doc_id"] for hit in hits]
            rank = doc_ids.index(expected) + 1 if expected in doc_ids else None

            r1 += rank == 1
            r3 += rank is not None and rank <= 3
            r5 += rank is not None and rank <= 5

            if rank:
                mrr += 1 / rank
            else:
                misses.append(q["id"])

            if q["kind"] == "exact-id":
                exact_total += 1
                exact_r1 += rank == 1

            print(f'{q["id"]}: expected={expected} rank={rank} top={doc_ids[0]} reranker={hits[0]["reranker_score"]:.3f}')
        else:
            print(f'{q["id"]}: unanswerable top={hits[0]["doc_id"]} reranker={hits[0]["reranker_score"]:.3f}')

    answerable = [q for q in EVAL_SET if q["doc_id"]]

    print("\nAzure retrieval")
    print(f"Questions:       {len(answerable)}")
    print(f"Embedding tokens:{tokens}")
    print(f"Recall@1:        {r1 / len(answerable):.3f}")
    print(f"Recall@3:        {r3 / len(answerable):.3f}")
    print(f"Recall@5:        {r5 / len(answerable):.3f}")
    print(f"MRR:             {mrr / len(answerable):.3f}")
    print(f"Exact-ID R@1:    {exact_r1 / exact_total:.3f}")
    print(f"Misses:          {misses or 'none'}")

    print("\nSemantic reranker floors")

    answerable_total = sum(q["doc_id"] is not None for q in EVAL_SET)
    unanswerable_total = sum(q["doc_id"] is None for q in EVAL_SET)

    for floor in RERANK_FLOORS:
        accepted_answerable = 0
        refused_unanswerable = 0
        false_refusals = []
        false_accepts = []

        for result in results:
            q = result["question"]
            usable = [hit for hit in result["hits"] if hit["reranker_score"] is not None and hit["reranker_score"] >= floor]
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
            f"floor={floor:.1f} "
            f"answerable={accepted_answerable}/{answerable_total} "
            f"unanswerable_refused={refused_unanswerable}/{unanswerable_total} "
            f"false_refusals={false_refusals or 'none'} "
            f"false_accepts={false_accepts or 'none'}"
        )


if __name__ == "__main__":
    evaluate()