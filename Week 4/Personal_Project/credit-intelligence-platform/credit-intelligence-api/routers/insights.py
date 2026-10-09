from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from anthropic import APIStatusError, APITimeoutError, RateLimitError

import llm
from calculations import calculate_borrower_metrics
from routers.borrowers import get_borrower_or_404

router = APIRouter(prefix="/borrowers", tags=["insights"])


@router.get("/{borrower_id}/summary")
def borrower_summary(borrower_id: int):
    borrower = get_borrower_or_404(borrower_id)
    metrics = calculate_borrower_metrics(borrower)

    try:
        result = llm.summarise_borrower(borrower, metrics)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Credit analysis provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Credit analysis provider rate limited")
    except APIStatusError:
        raise HTTPException(status_code=502, detail="Credit analysis provider failed")

    return {"borrower_id": borrower_id, "borrower_name": borrower["name"], **result}

@router.get("/{borrower_id}/summary/stream")
def borrower_summary_stream(borrower_id: int):
    borrower = get_borrower_or_404(borrower_id)
    metrics = calculate_borrower_metrics(borrower)

    return StreamingResponse(llm.stream_borrower_summary(borrower, metrics), media_type="text/plain")


@router.get("/{borrower_id}/analysis")
def borrower_analysis(borrower_id: int):
    borrower = get_borrower_or_404(borrower_id)
    metrics = calculate_borrower_metrics(borrower)

    try:
        result = llm.analyse_borrower(borrower, metrics)
    except APITimeoutError:
        raise HTTPException(status_code=504, detail="Credit analysis provider timed out")
    except RateLimitError:
        raise HTTPException(status_code=429, detail="Credit analysis provider rate limited")
    except APIStatusError:
        raise HTTPException(status_code=502, detail="Credit analysis provider failed")

    return {"borrower_id": borrower_id, "borrower_name": borrower["name"], **result}