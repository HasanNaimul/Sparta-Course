from datetime import date

from safety import financial_age_days, is_financial_data_stale


def test_financial_age_days():
    age = financial_age_days("2026-01-01", as_of=date(2026, 7, 1))
    assert age == 181


def test_financial_data_over_180_days_is_stale():
    assert is_financial_data_stale("2026-01-01", 180, as_of=date(2026, 7, 1)) is True


def test_financial_data_at_180_days_is_not_stale():
    assert is_financial_data_stale("2026-01-02", 180, as_of=date(2026, 7, 1)) is False