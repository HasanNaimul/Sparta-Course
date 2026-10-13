"""Evaluate answer quality for the shortlisted retrieval strategies.

This file calls the model.
Maximum cost: one model call per question per strategy.
Results are saved to eval_results/answers.json.
"""

import argparse
import json
import statistics
from pathlib import Path

import chunk_index
import chunking
import context
import llm
from eval_set import EVAL_SET
from eval_tools import keywords_present
from grounding import REFUSAL_SENTENCE, is_refusal


def safe_mean(values) -> float:
    """Return the mean, or 0 if the list is empty."""
    values = list(values)
    return statistics.mean(values) if values else 0


def run(strategy: str, vectors: list[list[float]], floor: float) -> dict:
    """Evaluate answer and refusal quality for one retrieval strategy."""
    ranked = chunk_index.search_with_vectors(strategy, vectors, k=3)

    correct = []
    false_refusals = []
    wrong = []
    tokens = []

    for q, hits in zip(EVAL_SET, ranked):
        usable = [hit for hit in hits if hit["score"] >= floor]

        # Call Claude only when at least one retrieved chunk passes the floor.
        if usable:
            result = llm.answer_from_context(q["question"], context.build_context(usable))
            answer = result["answer"]
            tokens.append(result["input_tokens"])
        else:
            answer = REFUSAL_SENTENCE

        # Answerable: correct if expected keywords are present.
        # Unanswerable: correct if the system refuses.
        ok = keywords_present(answer, q["keywords"]) if q["doc_id"] else is_refusal(answer)
        correct.append((q, ok))

        if not ok:
            if q["doc_id"] and is_refusal(answer):
                false_refusals.append(q["id"])
            else:
                wrong.append(q["id"])

    answerable = [ok for q, ok in correct if q["doc_id"]]
    unanswerable = [ok for q, ok in correct if not q["doc_id"]]

    return {
        "answer_accuracy": round(safe_mean(answerable), 3),
        "refusal_accuracy": round(safe_mean(unanswerable), 3),
        "false_refusals": false_refusals,
        "wrong_or_unrefused": wrong,
        "model_calls": len(tokens),
        "avg_input_tokens": round(safe_mean(tokens)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate answer quality for shortlisted retrieval strategies.")
    parser.add_argument("strategies", nargs="+", choices=chunking.STRATEGIES)
    parser.add_argument("--floor", type=float, default=0.35)
    args = parser.parse_args()

    print("Building indexes (free if nothing has changed)...")

    for strategy in args.strategies:
        result = chunk_index.build(strategy)
        print(
            f"  {strategy:<22} {result['chunks']:>3} chunks  "
            f"{'rebuilt' if result['rebuilt'] else 'up to date':<10}  "
            f"{result['embedding_tokens']:>6} tokens"
        )

    vectors, embedding_tokens = chunk_index.embed_batched(
        [q["question"] for q in EVAL_SET],
        input_type="query",
    )

    print(
        f"\nEmbedded {len(EVAL_SET)} questions once "
        f"({embedding_tokens} tokens), reused for every strategy.\n"
    )

    results = {}

    for strategy in args.strategies:
        print(f"Evaluating {strategy}...")
        results[strategy] = run(strategy, vectors, args.floor)

    print(f"\nfloor = {args.floor}\n")

    header = f"{'strategy':<22}{'answers':>9}{'refusals':>10}{'calls':>7}{'avg in tokens':>15}"
    print(header)
    print("-" * len(header))

    for strategy, result in results.items():
        print(
            f"{strategy:<22}"
            f"{result['answer_accuracy']:>9.2f}"
            f"{result['refusal_accuracy']:>10.2f}"
            f"{result['model_calls']:>7}"
            f"{result['avg_input_tokens']:>15}"
        )
        print(f"    false refusals: {', '.join(result['false_refusals']) or 'none'}")
        print(f"    wrong or not refused: {', '.join(result['wrong_or_unrefused']) or 'none'}")

    Path("eval_results").mkdir(exist_ok=True)
    Path("eval_results/answers.json").write_text(
        json.dumps({"floor": args.floor, **results}, indent=2),
        encoding="utf-8",
    )

    print("\nSaved eval_results/answers.json")


if __name__ == "__main__":
    main()