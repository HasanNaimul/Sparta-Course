"""FastAPI v2 routes powered by LangGraph."""

from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import APIRouter, HTTPException
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field

import grounding
from v2.lc_graph import graph

router = APIRouter(prefix="/v2/knowledge", tags=["v2-knowledge"])


class Question(BaseModel):
    question: str = Field(min_length=3)


@router.post("/ask")
def ask(q: Question):
    try:
        result = graph.invoke({"messages": [("user", q.question)]})
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
            "answer": None,
            "refused": True,
            "reason": grounding.REFUSAL,
            "tools_used": tools_used,
        }

    return {
        "question": q.question,
        "answer": answer,
        "refused": False,
        "tools_used": tools_used,
    }