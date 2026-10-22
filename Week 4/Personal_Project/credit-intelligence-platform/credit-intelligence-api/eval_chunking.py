"""Compare Credit Intelligence chunking strategies using the same labelled questions."""

import math
import time

import voyageai

import chunking
import knowledge
from eval_set import EVAL_SET

BATCH_SIZE = 20
BATCH_PAUSE = 22
RETRY_SECONDS = 25
MAX_RETRIES = 6


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def embed_with_retry(texts: list[str], input_type: str) -> tuple[list[list[float]], int]:
    vectors, total_tokens = [], 0

    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start:start + BATCH_SIZE]
        batch_number = start // BATCH_SIZE + 1
        total_batches = math.ceil(len(texts) / BATCH_SIZE)

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                batch_vectors, tokens = knowledge.embed_texts(batch, input_type=input_type)
                vectors.extend(batch_vectors)
                total_tokens += tokens
                print(f"{input_type} batch {batch_number}/{total_batches} embedded ({tokens} tokens)")
                break
            except voyageai.error.RateLimitError:
                if attempt == MAX_RETRIES:
                    raise

                print(f"Voyage rate limit reached. Retrying in {RETRY_SECONDS} seconds...")
                time.sleep(RETRY_SECONDS)

        if start + BATCH_SIZE < len(texts):
            time.sleep(BATCH_PAUSE)

    return vectors, total_tokens


def evaluate() -> None:
    answerable = [q for q in EVAL_SET if q["doc_id"]]
    chunks_by_strategy = {strategy: chunking.chunk_corpus(strategy) for strategy in chunking.STRATEGIES}

    all_chunks, ranges = [], {}
    start = 0

    for strategy, chunks in chunks_by_strategy.items():
        all_chunks.extend(chunks)
        ranges[strategy] = (start, start + len(chunks))
        start += len(chunks)

    print("Chunk counts")
    for strategy, chunks in chunks_by_strategy.items():
        print(f"{strategy:24} {len(chunks)}")

    chunk_texts = [chunk["text"] for chunk in all_chunks]
    questions = [q["question"] for q in answerable]

    print("\nEmbedding document chunks...")
    chunk_vectors, chunk_tokens = embed_with_retry(chunk_texts, "document")

    print("\nEmbedding evaluation questions...")
    query_vectors, query_tokens = embed_with_retry(questions, "query")

    print(f"\nEmbedding tokens: chunks={chunk_tokens}, queries={query_tokens}, total={chunk_tokens + query_tokens}")

    for strategy in chunking.STRATEGIES:
        start, end = ranges[strategy]
        chunks = all_chunks[start:end]
        vectors = chunk_vectors[start:end]

        recall_1 = recall_3 = recall_5 = 0
        reciprocal_rank = 0.0
        context_words = 0
        exact_total = exact_recall_1 = 0
        misses = []

        for q, query_vector in zip(answerable, query_vectors):
            ranked = sorted(zip(chunks, vectors), key=lambda pair: cosine(query_vector, pair[1]), reverse=True)
            top5 = ranked[:5]

            doc_ids = [chunk["doc_id"] for chunk, _ in top5]
            expected = q["doc_id"]
            rank = doc_ids.index(expected) + 1 if expected in doc_ids else None

            recall_1 += rank == 1
            recall_3 += rank is not None and rank <= 3
            recall_5 += rank is not None and rank <= 5

            if rank:
                reciprocal_rank += 1 / rank
            else:
                misses.append(q["id"])

            context_words += sum(len(chunk["text"].split()) for chunk, _ in ranked[:3])

            if q["kind"] == "exact-id":
                exact_total += 1
                exact_recall_1 += rank == 1

        total = len(answerable)

        print(f"\n{strategy}")
        print(f"  Recall@1:        {recall_1 / total:.3f}")
        print(f"  Recall@3:        {recall_3 / total:.3f}")
        print(f"  Recall@5:        {recall_5 / total:.3f}")
        print(f"  MRR:             {reciprocal_rank / total:.3f}")
        print(f"  Context words@3: {context_words / total:.0f}")
        print(f"  Exact-ID R@1:    {exact_recall_1 / exact_total:.3f}" if exact_total else "  Exact-ID R@1:    n/a")
        print(f"  Misses:          {misses or 'none'}")


if __name__ == "__main__":
    evaluate()