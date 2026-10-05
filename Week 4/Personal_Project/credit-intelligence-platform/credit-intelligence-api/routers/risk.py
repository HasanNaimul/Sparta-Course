from fastapi import APIRouter, HTTPException

from calculations import calculate_borrower_metrics, evaluate_covenant
from data import FACILITIES, COVENANTS
from models import StressScenario
from routers.borrowers import get_borrower_or_404

router = APIRouter(prefix="/borrowers", tags=["risk"])


@router.post("/{borrower_id}/stress-test")
def stress_test(borrower_id: int, scenario: StressScenario):
    borrower = get_borrower_or_404(borrower_id)
    metrics = calculate_borrower_metrics(borrower, scenario.ebitda_shock_pct)

    facilities = [f for f in FACILITIES if f["borrower_id"] == borrower_id]
    facility_ids = {f["id"] for f in facilities}
    covenants = [c for c in COVENANTS if c["facility_id"] in facility_ids]

    if not covenants:
        raise HTTPException(status_code=404, detail="No covenants found for borrower")

    results = []

    for covenant in covenants:
        if covenant["metric"] == "net_leverage":
            current_value = metrics["current_net_leverage"]
            stressed_value = metrics["stressed_net_leverage"]
        else:
            current_value = metrics["current_interest_cover"]
            stressed_value = metrics["stressed_interest_cover"]

        current = evaluate_covenant(current_value, covenant["threshold"], covenant["comparison"])
        stressed = evaluate_covenant(stressed_value, covenant["threshold"], covenant["comparison"])

        results.append({
            "covenant_id": covenant["id"],
            "facility_id": covenant["facility_id"],
            "metric": covenant["metric"],
            "threshold": covenant["threshold"],
            "comparison": covenant["comparison"],
            "current_value": current_value,
            "stressed_value": stressed_value,
            "current_headroom": current["headroom"],
            "stressed_headroom": stressed["headroom"],
            "current_status": current["status"],
            "stressed_status": stressed["status"],
        })

    return {
        "borrower_id": borrower["id"],
        "borrower_name": borrower["name"],
        "ebitda_shock_pct": scenario.ebitda_shock_pct,
        "metrics": metrics,
        "covenants": results,
    }