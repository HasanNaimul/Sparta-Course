import pytest

from calculations import (
    apply_ebitda_stress,
    calculate_borrower_metrics,
    calculate_interest_cover,
    calculate_net_debt,
    calculate_net_leverage,
)
from data import BORROWERS


def test_net_debt():
    assert calculate_net_debt(245, 38) == 207


def test_net_leverage():
    result = calculate_net_leverage(207, 82)

    assert result == pytest.approx(2.524, rel=0.01,)


def test_interest_cover():
    result = calculate_interest_cover(82, 24)

    assert result == pytest.approx(3.417, rel=0.01,)


def test_ebitda_stress():
    result = apply_ebitda_stress(100, -20,)

    assert result == 80


def test_northbridge_20_percent_stress():
    result = calculate_borrower_metrics(
        BORROWERS[0], -20,)

    assert result["current_net_leverage"] == 2.52
    assert result["stressed_net_leverage"] == 3.16


def test_asteron_20_percent_stress():
    result = calculate_borrower_metrics(
        BORROWERS[2], -20,)

    assert result["current_net_leverage"] == 3.96
    assert result["stressed_net_leverage"] == 4.95


def test_zero_ebitda_is_rejected():
    with pytest.raises( ValueError, match="EBITDA must be greater than zero",):
        calculate_net_leverage(100, 0,)