from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

import gate
import grounding
import knowledge_store
import llm
from config import settings

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class Question(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=3, gt=0, le=8)


@router.post("/index")
def rebuild_index():
    try:
        tokens = knowledge_store.build_index()
    except RuntimeError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return {
        "indexed": knowledge_store.count(),
        "embedding_tokens": tokens,
    }


@router.post("/search")
def search(q: Question):
    try:
        hits = knowledge_store.search(q.question, q.top_k)
    except RuntimeError as error:
        raise HTTPException(status_code=409, detail=str(error))

    return {
        "question": q.question,
        "results": hits,
    }


@router.post("/ask")
def ask(q: Question):
    try:
        hits = knowledge_store.search(q.question, q.top_k)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))

    usable = [hit for hit in hits if gate.is_usable(hit, settings.relevance_floor)]

    if not usable:
        return {
            "question": q.question,
            "answer": None,
            "refused": True,
            "reason": "No retrieved document passed the relevance gate.",
            "sources": [],
        }

    retrieved_context = grounding.build_context(usable)

    try:
        result = llm.answer_from_context(q.question, retrieved_context)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Answer provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Answer provider rate limited")
    except APIStatusError:
        raise HTTPException(status_code=502, detail="Answer provider service failed")

    if grounding.is_refusal(result["answer"]):
        return {
            "question": q.question,
            "answer": None,
            "refused": True,
            "reason": grounding.REFUSAL,
            "sources": [],
        }

    return {
        "question": q.question,
        "answer": result["answer"],
        "refused": False,
        "sources": [
            {
                "id": hit["doc_id"],
                "title": hit["title"],
                "score": round(hit["score"], 3) if hit.get("score") is not None else None,
            }
            for hit in usable
        ],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "stop_reason": result["stop_reason"],
    }