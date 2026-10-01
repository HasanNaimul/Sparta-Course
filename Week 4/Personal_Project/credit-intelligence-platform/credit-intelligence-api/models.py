from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class BorrowerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    sector: str = Field(min_length=2, max_length=60)
    country: str = Field(min_length=2, max_length=60)

    internal_risk_band: Literal["low", "moderate", "elevated","high",]

    revenue_m: float = Field(gt=0)
    ebitda_m: float = Field(gt=0)
    total_debt_m: float = Field(ge=0)
    cash_m: float = Field(ge=0)
    interest_expense_m: float = Field(gt=0)

    last_financials_date: date
    watchlist: bool = False


class FacilityCreate(BaseModel):
    borrower_id: int = Field(gt=0)

    facility_type: Literal["revolving_credit", "term_loan", "acquisition_facility",]

    currency: Literal["GBP", "USD", "EUR",]

    committed_amount_m: float = Field(gt=0)
    drawn_amount_m: float = Field(ge=0)

    margin_bps: int = Field(gt=0)

    maturity_date: date
    secured: bool


class CovenantCreate(BaseModel):
    facility_id: int = Field(gt=0)

    metric: Literal["net_leverage","interest_cover",]

    threshold: float = Field(gt=0)

    comparison: Literal["maximum","minimum",]

    testing_frequency: Literal["quarterly","semi_annual","annual",]

    last_test_date: date