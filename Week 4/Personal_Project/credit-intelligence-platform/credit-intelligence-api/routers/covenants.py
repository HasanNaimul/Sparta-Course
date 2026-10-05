from fastapi import APIRouter, HTTPException

from data import COVENANTS
from models import CovenantCreate
from routers.facilities import get_facility_or_404


router = APIRouter(prefix="/covenants",tags=["covenants"],)


def get_covenant_or_404(covenant_id: int) -> dict:
    for covenant in COVENANTS:
        if covenant["id"] == covenant_id:
            return covenant

    raise HTTPException(status_code=404,detail="Covenant not found",)


@router.get("")
def list_covenants(
    facility_id: int | None = None,
    metric: str | None = None,
):
    results = COVENANTS

    if facility_id is not None:
        results = [
            covenant
            for covenant in results
            if covenant["facility_id"] == facility_id
        ]

    if metric is not None:
        results = [
            covenant
            for covenant in results
            if covenant["metric"].lower() == metric.lower()
        ]

    return results


@router.get("/{covenant_id}")
def get_covenant(covenant_id: int):
    return get_covenant_or_404(covenant_id)


@router.post("", status_code=201)
def create_covenant(new: CovenantCreate):

    # Make sure the facility exists
    get_facility_or_404(new.facility_id)

    next_id = max(
        covenant["id"]
        for covenant in COVENANTS
    ) + 1

    covenant = {
        "id": next_id,
        **new.model_dump(mode="json"),
    }

    COVENANTS.append(covenant)

    return covenant


@router.put("/{covenant_id}")
def update_covenant(covenant_id: int,new: CovenantCreate,):
    covenant = get_covenant_or_404(covenant_id)

    # Make sure the new facility_id exists
    get_facility_or_404(new.facility_id)

    covenant.update(
        new.model_dump(mode="json")
    )

    return covenant


@router.delete("/{covenant_id}",status_code=204,)
def delete_covenant(covenant_id: int):
    covenant = get_covenant_or_404(
        covenant_id
    )

    COVENANTS.remove(covenant)