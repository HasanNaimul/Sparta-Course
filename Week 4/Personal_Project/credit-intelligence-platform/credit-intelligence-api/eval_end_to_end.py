"""Evaluate the final local Credit Intelligence RAG pipeline."""

import time

import voyageai
from anthropic import APITimeoutError, RateLimitError

import gate
import grounding
import hybrid
import knowledge
import llm
from eval_set import EVAL_SET

STRATEGY = "title_contextual_100"
TOP_K = 5
RELEVANCE_FLOOR = 0.35

BATCH_SIZE = 20
BATCH_PAUSE = 22
VOYAGE_RETRY_SECONDS = 25
LLM_RETRY_SECONDS = 20
MAX_RETRIES = 6


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
                print(f"Voyage rate limit reached. Retrying in {VOYAGE_RETRY_SECONDS} seconds...")
                time.sleep(VOYAGE_RETRY_SECONDS)

        if start + BATCH_SIZE < len(questions):
            time.sleep(BATCH_PAUSE)

    return vectors, total_tokens


def answer_with_retry(question: str, context: str) -> dict:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return llm.answer_from_context(question, context)
        except (RateLimitError, APITimeoutError):
            if attempt == MAX_RETRIES:
                raise
            print(f"Claude unavailable. Retrying in {LLM_RETRY_SECONDS} seconds...")
            time.sleep(LLM_RETRY_SECONDS)

    raise RuntimeError("LLM call failed")


def keyword_match(answer: str, keywords: list[str]) -> bool:
    text = answer.lower()
    return all(keyword.lower() in text for keyword in keywords)


def evaluate() -> None:
    query_vectors, embedding_tokens = embed_queries([q["question"] for q in EVAL_SET])

    correct_answers = 0
    correct_refusals = 0
    false_refusals = []
    wrong_answers = []
    false_accepts = []

    answerable_total = sum(q["doc_id"] is not None for q in EVAL_SET)
    unanswerable_total = sum(q["doc_id"] is None for q in EVAL_SET)

    input_tokens = output_tokens = calls = context_words = 0

    for q, vector in zip(EVAL_SET, query_vectors):
        hits = hybrid.search_with_vector(q["question"], vector, top_k=TOP_K, strategy=STRATEGY)
        usable = [hit for hit in hits if gate.is_usable(hit, RELEVANCE_FLOOR)]

        if not usable:
            if q["doc_id"]:
                false_refusals.append(q["id"])
                print(f'{q["id"]}: FALSE REFUSAL (gate)')
            else:
                correct_refusals += 1
                print(f'{q["id"]}: REFUSED (gate)')
            continue

        context = grounding.build_context(usable)
        context_words += len(context.split())

        result = answer_with_retry(q["question"], context)
        calls += 1
        input_tokens += result["input_tokens"]
        output_tokens += result["output_tokens"]

        answer = result["answer"].strip()
        refused = grounding.is_refusal(answer)

        if q["doc_id"]:
            if refused:
                false_refusals.append(q["id"])
                status = "FALSE REFUSAL"
            elif keyword_match(answer, q["keywords"]):
                correct_answers += 1
                status = "CORRECT"
            else:
                wrong_answers.append(q["id"])
                status = "WRONG"
        else:
            if refused:
                correct_refusals += 1
                status = "REFUSED"
            else:
                false_accepts.append(q["id"])
                status = "FALSE ACCEPT"

        print(f'{q["id"]}: {status}')

    print("\nResults")
    print(f"Answer accuracy:  {correct_answers / answerable_total:.3f} ({correct_answers}/{answerable_total})")
    print(f"Refusal accuracy: {correct_refusals / unanswerable_total:.3f} ({correct_refusals}/{unanswerable_total})")
    print(f"False refusals:   {false_refusals or 'none'}")
    print(f"Wrong answers:    {wrong_answers or 'none'}")
    print(f"False accepts:    {false_accepts or 'none'}")
    print(f"Embedding tokens: {embedding_tokens}")
    print(f"LLM calls:        {calls}")

    if calls:
        print(f"Avg input tokens: {input_tokens / calls:.0f}")
        print(f"Avg output tokens:{output_tokens / calls:.0f}")
        print(f"Avg context words:{context_words / calls:.0f}")


if __name__ == "__main__":
    evaluate()