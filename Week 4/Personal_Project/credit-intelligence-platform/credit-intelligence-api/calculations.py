def calculate_net_debt(
    total_debt_m: float, cash_m: float,
) -> float:
    """Calculate net debt in millions."""

    return total_debt_m - cash_m


def calculate_net_leverage(
    net_debt_m: float, ebitda_m: float,
) -> float:
    """Calculate net debt divided by EBITDA."""

    if ebitda_m <= 0:
        raise ValueError("EBITDA must be greater than zero")

    return net_debt_m / ebitda_m


def calculate_interest_cover(
    ebitda_m: float, interest_expense_m: float,
) -> float:
    """Calculate EBITDA divided by interest expense."""

    if interest_expense_m <= 0:
        raise ValueError(
            "Interest expense must be greater than zero"
        )

    return ebitda_m / interest_expense_m


def apply_ebitda_stress(
    ebitda_m: float, shock_pct: float,
) -> float:
    """
    Apply an EBITDA percentage shock.

    Example:
    100 EBITDA with -20% shock becomes 80.
    """

    stressed_ebitda = ebitda_m * (1 + shock_pct / 100)

    if stressed_ebitda <= 0:
        raise ValueError(
            "Stress scenario results in EBITDA of zero or below"
        )

    return stressed_ebitda


def calculate_borrower_metrics( borrower: dict, ebitda_shock_pct: float = 0,
) -> dict:
    """Calculate current and stressed credit metrics."""

    net_debt = calculate_net_debt( borrower["total_debt_m"], borrower["cash_m"],)

    current_leverage = calculate_net_leverage( net_debt, borrower["ebitda_m"],)

    current_interest_cover = calculate_interest_cover( borrower["ebitda_m"], borrower["interest_expense_m"],)

    stressed_ebitda = apply_ebitda_stress(borrower["ebitda_m"], ebitda_shock_pct,)

    stressed_leverage = calculate_net_leverage(net_debt, stressed_ebitda,)

    stressed_interest_cover = calculate_interest_cover(stressed_ebitda, borrower["interest_expense_m"],)

    return {
        "borrower_id": borrower["id"],
        "borrower_name": borrower["name"],
        "ebitda_shock_pct": ebitda_shock_pct,
        "net_debt_m": round(net_debt, 2),
        "current_ebitda_m": round(
            borrower["ebitda_m"],
            2,
        ),
        "stressed_ebitda_m": round(
            stressed_ebitda,
            2,
        ),
        "current_net_leverage": round(
            current_leverage,
            2,
        ),
        "stressed_net_leverage": round(
            stressed_leverage,
            2,
        ),
        "current_interest_cover": round(
            current_interest_cover,
            2,
        ),
        "stressed_interest_cover": round(
            stressed_interest_cover,
            2,
        ),
    }


