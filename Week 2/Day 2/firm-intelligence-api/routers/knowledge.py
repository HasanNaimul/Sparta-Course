from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from anthropic import APIStatusError, APITimeoutError, RateLimitError

import gate
import grounding
import llm
import settings
from routers import knowledge_store as knowledge

RELEVANCE_FLOOR = 0.45

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class Question(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=3, gt=0, le=8)


@router.post("/index")
def rebuild_index():
    """Embed the corpus deliberately and store it in the local index."""
    try:
        tokens = knowledge.build_index()
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {
        "indexed": knowledge.count(),
        "embedding_tokens": tokens,
    }


@router.post("/search")
def search(q: Question):
    """Retrieval only. No model call or generated text."""
    try:
        results = knowledge.search(q.question, q.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {
        "question": q.question,
        "results": results,
    }


@router.post("/ask")
def ask(q: Question):
    """Retrieve, then answer using only what was retrieved, or refuse."""
    try:
        hits = knowledge.search(q.question, q.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    usable = [
        hit
        for hit in hits
        if gate.is_usable(hit, RELEVANCE_FLOOR, settings.RERANK_FLOOR)
    ]

    if not usable:
        return {
            "question": q.question,
            "answer": None,
            "refused": True,
            "reason": "No document in the corpus is relevant to that question.",
            "sources": [],
        }

    retrieved_context = "\n\n".join(
        f"[{h['id']}] {h['title']}\n{h['text']}"
        for h in usable
    )

    try:
        result = llm.answer_from_context(q.question, retrieved_context)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Answer provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Answer provider rate limited")
    except APIStatusError:
        raise HTTPException(status_code=502, detail="Answer provider service failed")

    sources = []

    for hit in usable:
        source = {
            "id": hit["id"],
            "title": hit["title"],
            "score": round(hit["score"], 3),
        }

        if hit.get("reranker_score") is not None:
            source["reranker_score"] = round(hit["reranker_score"], 3)

        if hit.get("rrf") is not None:
            source["rrf"] = hit["rrf"]

        sources.append(source)

    return {
        "question": q.question,
        "answer": result["answer"],
        "refused": False,
        "sources": sources,
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "stop_reason": result["stop_reason"],
        "grounding": grounding.check_citations(
            result["answer"],
            [h["id"] for h in usable],
        ),
    }