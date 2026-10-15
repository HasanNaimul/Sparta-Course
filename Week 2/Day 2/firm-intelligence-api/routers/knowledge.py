from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from anthropic import APIStatusError, APITimeoutError, RateLimitError

import grounding
import hybrid
import llm
from routers import knowledge_store as knowledge

RELEVANCE_FLOOR = 0.35

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class Question(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=3, gt=0, le=8)


@router.post("/index")
def rebuild_index():
    """Embed the corpus deliberately and store it in ChromaDB."""
    tokens = knowledge.build_index()
    return {"indexed": knowledge.count(), "embedding_tokens": tokens}


@router.post("/search")
def search(q: Question):
    """Retrieval only. No model call or generated text."""
    try:
        return {"question": q.question, "results": knowledge.search(q.question, q.top_k)}
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/ask")
def ask(q: Question):
    """Retrieve, then answer using only what was retrieved, or refuse."""
    try:
        hits = knowledge.search(q.question, q.top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    usable = [hit for hit in hits if hybrid.is_usable(hit, RELEVANCE_FLOOR)]

    if not usable:
        return {
            "question": q.question,
            "answer": None,
            "refused": True,
            "reason": "No document in the corpus is relevant to that question.",
            "sources": [],
        }

    context = "\n\n".join(f"[{h['id']}] {h['title']}\n{h['text']}" for h in usable)

    try:
        result = llm.answer_from_context(q.question, context)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Answer provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Answer provider rate limited")
    except APIStatusError:
        raise HTTPException(status_code=502, detail="Answer provider service failed")

    return {
        "question": q.question,
        "answer": result["answer"],
        "refused": False,
        "sources": [{"id": h["id"], "title": h["title"], "score": round(h["score"], 3)} for h in usable],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "stop_reason": result["stop_reason"],
        "grounding": grounding.check_citations(result["answer"], [h["id"] for h in usable]),
    }