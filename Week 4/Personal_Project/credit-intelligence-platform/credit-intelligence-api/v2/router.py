"""FastAPI v2 routes powered by LangGraph."""

from uuid import uuid4

from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import APIRouter, HTTPException
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field

import grounding
from v2.lc_graph import graph

router = APIRouter(prefix="/v2/knowledge", tags=["v2-knowledge"])


class Question(BaseModel):
    question: str = Field(min_length=3)
    thread_id: str | None = Field(default=None, max_length=100)


@router.post("/ask")
def ask(q: Question):
    thread_id = q.thread_id or str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        result = graph.invoke({"messages": [("user", q.question)]}, config)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Answer provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Answer provider rate limited")
    except APIStatusError:
        raise HTTPException(status_code=502, detail="Answer provider service failed")
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))

    messages = result["messages"]
    answer = messages[-1].content.strip()
    tools_used = [message.name for message in messages if isinstance(message, ToolMessage)]

    if grounding.is_refusal(answer):
        return {
            "question": q.question,
            "thread_id": thread_id,
            "answer": None,
            "refused": True,
            "reason": grounding.REFUSAL,
            "tools_used": tools_used,
        }

    return {
        "question": q.question,
        "thread_id": thread_id,
        "answer": answer,
        "refused": False,
        "tools_used": tools_used,
    }