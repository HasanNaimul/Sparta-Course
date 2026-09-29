from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from anthropic import APIStatusError, APITimeoutError, RateLimitError

from routers import knowledge_store as knowledge
import llm


# Below this score, retrieved context is treated as not relevant
RELEVANCE_FLOOR = 0.1


router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"]
)


class Question(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=3, gt=0, le=8)


@router.post("/index")
def rebuild_index():
    """Embed the corpus deliberately and store it in ChromaDB."""

    tokens = knowledge.build_index()

    return {
        "indexed": knowledge.collection.count(),
        "embedding_tokens": tokens,
    }


@router.post("/search")
def search(q: Question):
    """Retrieval only. No model call or generated text."""

    try:
        return {
            "question": q.question,
            "results": knowledge.search(
                q.question,
                q.top_k
            ),
        }

    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )


# Function behaviour:
#
# - The refusal happens BEFORE the model is called, not after.
#
# - Why 200 and not 404 for a refusal?
#   The request was valid and the service handled it correctly.
#   "We have no relevant document" is a valid response.
#
# - Sources make the answer checkable.
#   Without sources, the client has to trust the generated answer.
#   With sources, they can open the document and verify the claim.
#
# - Same upstream error mapping as before:
#   504 = timeout
#   429 = rate limited
#   502 = provider/API failure


@router.post("/ask")
def ask(q: Question):
    """Retrieve, then answer using only what was retrieved, or refuse."""

    try:
        # 1. Retrieve the most similar documents
        hits = knowledge.search(
            q.question,
            q.top_k
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
        )

    # 2. Keep only documents above the relevance threshold
    usable = [
        hit
        for hit in hits
        if hit["score"] >= RELEVANCE_FLOOR
    ]

    # Refuse before calling the LLM if nothing is relevant
    if not usable:
        return {
            "question": q.question,
            "answer": None,
            "refused": True,
            "reason": "No document in the corpus is relevant to that question.",
            "sources": []
        }

    # 3. Build grounded context for the LLM
    context = "\n\n".join(
        f"[{h['id']}] {h['title']}\n{h['text']}"
        for h in usable
    )

    # 4. Ask the LLM using only the retrieved context
    try:
        result = llm.answer_from_context(
            q.question,
            context
        )

    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Answer provider timed out"
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Answer provider rate limited"
        )

    except APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="Answer provider service failed"
        )

    # 5. Return grounded answer plus sources and token usage
    return {
        "question": q.question,
        "answer": result["answer"],
        "refused": False,
        "sources": [
            {
                "id": h["id"],
                "title": h["title"],
                "score": round(h["score"], 3)
            }
            for h in usable
        ],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "stop_reason": result["stop_reason"],
    }