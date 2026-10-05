from fastapi import APIRouter, HTTPException

from data import BORROWERS
from models import BorrowerCreate


router = APIRouter(prefix="/borrowers",tags=["borrowers"],)


def get_borrower_or_404(borrower_id: int) -> dict:
    for borrower in BORROWERS:
        if borrower["id"] == borrower_id:
            return borrower

    raise HTTPException(status_code=404,detail="Borrower not found",)


@router.get("")
def list_borrowers(
    sector: str | None = None,
    watchlist: bool | None = None,
):
    results = BORROWERS

    if sector is not None:
        results = [
            borrower
            for borrower in results
            if borrower["sector"].lower() == sector.lower()
        ]

    if watchlist is not None:
        results = [
            borrower
            for borrower in results
            if borrower["watchlist"] == watchlist
        ]

    return results


@router.get("/{borrower_id}")
def get_borrower(borrower_id: int):
    return get_borrower_or_404(borrower_id)


@router.post("", status_code=201)
def create_borrower(new: BorrowerCreate):
    next_id = max(
        borrower["id"]
        for borrower in BORROWERS
    ) + 1

    borrower = {
        "id": next_id,
        **new.model_dump(mode="json"),
    }

    BORROWERS.append(borrower)

    return borrower


@router.put("/{borrower_id}")
def update_borrower(borrower_id: int,new: BorrowerCreate,):
    borrower = get_borrower_or_404(borrower_id)

    borrower.update(new.model_dump(mode="json"))

    return borrower


@router.delete("/{borrower_id}",status_code=204,)
def delete_borrower(borrower_id: int):
    borrower = get_borrower_or_404(
        borrower_id
    )

    BORROWERS.remove(borrower)