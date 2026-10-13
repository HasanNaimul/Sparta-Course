"""Build the retrieval scoreboard.

Score every chunking strategy against the evaluation set.
Build all 6 indexes -> embed the questions once -> search every index -> score -> print + save.
"""

import json
import statistics
from pathlib import Path

import chunk_index
import chunking
from eval_set import EVAL_SET
from eval_tools import contains_evidence

# Look at the top 1, 3 and 5 results.
K_VALUES = (1, 3, 5)


def first_hit_rank(hits: list[dict], evidence: str) -> int | None:
    """Return the rank of the first chunk containing the full evidence span."""
    for rank, hit in enumerate(hits, start=1):
        if contains_evidence(hit["text"], evidence):
            return rank
    return None


def safe_mean(values) -> float:
    """Return the mean, or 0 if there are no values."""
    values = list(values)
    return statistics.mean(values) if values else 0


def score_strategy(questions: list[dict], ranked: list[list[dict]]) -> dict:
    """Calculate Recall@k, MRR, context size and misses for one strategy."""

    answerable = [(q, hits) for q, hits in zip(questions, ranked) if q["doc_id"]]
    unanswerable = [(q, hits) for q, hits in zip(questions, ranked) if not q["doc_id"]]

    ranks = [first_hit_rank(hits, q["evidence"]) for q, hits in answerable]

    # Group Recall@3 by question kind.
    kinds: dict[str, list[bool]] = {}

    for (q, _), rank in zip(answerable, ranks):
        kinds.setdefault(q["kind"], []).append(rank is not None and rank <= 3)

    return {
        **{
            f"recall@{k}": round(safe_mean(r is not None and r <= k for r in ranks), 3)
            for k in K_VALUES
        },
        "mrr": round(safe_mean(1 / r if r else 0 for r in ranks), 3),
        "context_words@3": round(
            safe_mean(sum(len(hit["text"].split()) for hit in hits[:3]) for _, hits in answerable)
        ),
        "top_score_answerable": round(
            safe_mean(hits[0]["score"] for _, hits in answerable if hits), 3
        ),
        "top_score_unanswerable": round(
            safe_mean(hits[0]["score"] for _, hits in unanswerable if hits), 3
        ),
        "recall@3_by_kind": {
            kind: round(safe_mean(values), 2)
            for kind, values in sorted(kinds.items())
        },
        "missed@3": [
            q["id"]
            for (q, _), rank in zip(answerable, ranks)
            if rank is None or rank > 3
        ],
    }


def main() -> None:
    print("Building indexes (free if nothing has changed)...")

    for strategy in chunking.STRATEGIES:
        build_result = chunk_index.build(strategy)

        print(
            f"  {strategy:<22} {build_result['chunks']:>3} chunks  "
            f"{'rebuilt' if build_result['rebuilt'] else 'up to date':<10}  "
            f"{build_result['embedding_tokens']:>6} tokens"
        )

    vectors, tokens = chunk_index.embed_batched(
        [q["question"] for q in EVAL_SET],
        input_type="query",
    )

    print(
        f"\nEmbedded {len(EVAL_SET)} questions once ({tokens} tokens), "
        "reused for every strategy.\n"
    )

    results = {}

    for strategy in chunking.STRATEGIES:
        ranked = chunk_index.search_with_vectors(strategy, vectors, k=max(K_VALUES))
        results[strategy] = score_strategy(EVAL_SET, ranked)

    header = (
        f"{'strategy':<22}"
        f"{'R@1':>6}"
        f"{'R@3':>6}"
        f"{'R@5':>6}"
        f"{'MRR':>7}"
        f"{'ctx words':>11}"
        f"{'top ans':>9}"
        f"{'top unans':>11}"
    )

    print(header)
    print("-" * len(header))

    for strategy, result in results.items():
        print(
            f"{strategy:<22}"
            f"{result['recall@1']:>6.2f}"
            f"{result['recall@3']:>6.2f}"
            f"{result['recall@5']:>6.2f}"
            f"{result['mrr']:>7.2f}"
            f"{result['context_words@3']:>11}"
            f"{result['top_score_answerable']:>9.2f}"
            f"{result['top_score_unanswerable']:>11.2f}"
        )

    print("\nMissed at k=3:")

    for strategy, result in results.items():
        print(f"  {strategy:<22} {', '.join(result['missed@3']) or 'none'}")

    Path("eval_results").mkdir(exist_ok=True)
    Path("eval_results/retrieval.json").write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print("\nSaved eval_results/retrieval.json")


if __name__ == "__main__":
    main()