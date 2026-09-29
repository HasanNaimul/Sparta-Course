from fastapi import Depends, APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from data import FIRMS

router = APIRouter(prefix="/firms", tags=["firms"]) 
_seen_keys: dict[str, dict] = {}

#everything so far has been read-oly .... now somebody sends you data and you have no idea what it is

#First, we need to descibe what you will accept (shape)
class NewFirm(BaseModel):
    name: str = Field(min_length=1)
    jurisdiction: str = Field(min_length=1, max_length=5)
    revenue_usd_m: float = Field(gt=0)
    lawyers: int = Field(gt=0)
    equity_partners: int = Field(gt=0)

#a parameter annotated with a Pydantic model means body
# a plan int or str means a URL or query parameter 

def get_firm_or_404(firm_id: int):
    for firm in FIRMS:
        if firm["id"] == firm_id:
            return firm

    raise HTTPException(
        status_code=404,
        detail=f"No firm with id {firm_id}"
    )




# list firms always return everything
#add two optional query parameters (not a path parameter)

@router.get("")
def list_firms(
    jurisdiction: str | None = None,
    min_revenue: float | None = None
):
    results = FIRMS

    if jurisdiction is not None:
        results = [
            firm for firm in results
            if firm["jurisdiction"] == jurisdiction
        ]

    if min_revenue is not None:
        results = [
            firm for firm in results
            if firm["revenue_usd_m"] >= min_revenue
        ]

    return results


@router.get("/{firm_id}")
def get_firm(firm_id: dict = Depends(get_firm_or_404)):
    return firm_id

# compute revenue per lawyer is total revenue dicided by fee-earner headcount
    #profit per equity partner assemes a 35% margin, then divides by the number of equity
    # both are pretty standard law firm benchmarks... the kind of things Centellic platforms provide

@router.get("/{firm_id}/benchmarks")
def get_benchmarks(firm: dict = Depends(get_firm_or_404)):

    revenue = firm["revenue_usd_m"]

    return {
        "id": firm["id"],
        "name": firm["name"],
        "revenue_per_lawyer": round(
            revenue * 1_000_000 / firm["lawyers"],
            2
        ),
        "profit_per_equity_partner": round(
            revenue * 1_000_000 * 0.35 / firm["equity_partners"],
            2
        ),
    }




#post
#/firms
@router.post("", status_code=201)
def add_firm(new: NewFirm):
    new_id = max(firm["id"] for firm in FIRMS) + 1
    firm = {
        "id": new_id,
        "name": new.name,
        "jurisdiction": new.jurisdiction,
        "revenue_usd_m": new.revenue_usd_m,
        "lawyers": new.lawyers,
        "equity_partners": new.equity_partners
    }
    FIRMS.append(firm)
    return firm


@router.post("", status_code=201)
def add_firm(new: NewFirm, idempotency_key: str | None = Header(default=None)):
    if idempotency_key is not None and idempotency_key in _seen_keys:
        return _seen_keys[idempotency_key]
    
    new_id = max(firm["id"] for firm in FIRMS) + 1
    firm = {
        "id": new_id,
        "name": new.name,
        "jurisdiction": new.jurisdiction,
        "revenue_usd_m": new.revenue_usd_m,
        "lawyers": new.lawyers,
        "equity_partners": new.equity_partners
    }
    FIRM.append(firm)
    if idempotency_key is not None:
        _seen_keys[idempotency_key] = firm

    return firm

@router.put("/{firm_id}")
def update_firm(
    new: NewFirm,
    firm: dict = Depends(get_firm_or_404)
):
    firm.update(new.model_dump())
    return firm

#delete

@router.delete("/{firm_id}", status_code=204)
def delete_firm(firm: dict = Depends(get_firm_or_404)):
    FIRMS.remove(firm)
    return

