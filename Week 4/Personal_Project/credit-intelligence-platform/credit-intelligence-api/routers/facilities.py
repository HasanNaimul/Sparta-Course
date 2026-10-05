from fastapi import APIRouter, HTTPException

from data import FACILITIES
from models import FacilityCreate
from routers.borrowers import get_borrower_or_404


router = APIRouter(prefix="/facilities",tags=["facilities"],)


def get_facility_or_404(facility_id: int) -> dict:
    for facility in FACILITIES:
        if facility["id"] == facility_id:
            return facility

    raise HTTPException(status_code=404,detail="Facility not found",)


@router.get("")
def list_facilities(
    borrower_id: int | None = None,
    secured: bool | None = None,
):
    results = FACILITIES

    if borrower_id is not None:
        results = [
            facility
            for facility in results
            if facility["borrower_id"] == borrower_id
        ]

    if secured is not None:
        results = [
            facility
            for facility in results
            if facility["secured"] == secured
        ]

    return results


@router.get("/{facility_id}")
def get_facility(facility_id: int):
    return get_facility_or_404(facility_id)


@router.post("", status_code=201)
def create_facility(new: FacilityCreate):

    # Make sure the borrower actually exists
    get_borrower_or_404(new.borrower_id)

    next_id = max(
        facility["id"]
        for facility in FACILITIES
    ) + 1

    facility = {
        "id": next_id,
        **new.model_dump(mode="json"),
    }

    FACILITIES.append(facility)

    return facility


@router.put("/{facility_id}")
def update_facility(
    facility_id: int,
    new: FacilityCreate,
):
    facility = get_facility_or_404(
        facility_id
    )

    # Make sure the new borrower_id is valid
    get_borrower_or_404(new.borrower_id)

    facility.update(
        new.model_dump(mode="json")
    )

    return facility


@router.delete(
    "/{facility_id}",
    status_code=204,
)
def delete_facility(facility_id: int):
    facility = get_facility_or_404(
        facility_id
    )

    FACILITIES.remove(facility)