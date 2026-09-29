from anthropic import APIStatusError, APITimeoutError, RateLimitError
from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import llm
from routers.firms import get_firm_or_404


router = APIRouter(
    prefix="/firms", tags=["insights"]
)

@router.post("/{firm_id}/summary")
def create_summary(
    firm: dict = Depends(get_firm_or_404)
):
    try:
        return llm.summarise_firm(firm)

    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Upstream model timed out"
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Upstream model rate limited"
        )

    except APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="Upstream model service failed"
        )
# create a post endpoint for /firms/{firm_id}/summary
#it should take in a firm and find it (or not...)
#try to make the llm call to get a summary of the call
    #if unsuccessfull raise an appropriate Error and status code

#We added an AI summary endpoint for firms. FastAPI finds the firm, passes it to llm.py,
#  which calls Claude and returns a structured 
# result. We also translate Anthropic errors into
#  proper HTTP responses and keep token usage and 
# stop reason so we can tell whether the model 
# completed successfully.

@router.get("/{firm_id}/summary/estimate")
def estimate(firm: dict = Depends(get_firm_or_404)):
    return {
        "id": firm["id"],
        "estimated_input_tokens": llm.estimate_input_tokens(firm),
        "model": llm.MODEL,
    }

@router.get("/{firm_id}/summary/stream")
def stream_summary(firm: dict = Depends(get_firm_or_404)):
    return StreamingResponse(
        llm.stream_firm_summary(firm),
        media_type="text/plain",
    )


# endpoint challange
# post endpoint at firms/firm_id/analysis
# tries to analyse firm... if not, raises appropriate expeptions (s)
@router.post("/{firm_id}/analysis")
def analyse_firm(
    firm: dict = Depends(get_firm_or_404)
):
    try:
        return llm.analyse_firm(firm)

    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Upstream model timed out"
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Upstream model rate limited"
        )

    except APIStatusError:
        raise HTTPException(
            status_code=502,
            detail="Upstream model service failed"
        )