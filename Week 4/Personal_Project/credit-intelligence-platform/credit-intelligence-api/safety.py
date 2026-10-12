from datetime import date


def financial_age_days(last_financials_date: str | date, as_of: date | None = None) -> int:
    financial_date = date.fromisoformat(last_financials_date) if isinstance(last_financials_date, str) else last_financials_date
    today = as_of or date.today()
    return (today - financial_date).days


def is_financial_data_stale(last_financials_date: str | date, stale_days: int, as_of: date | None = None) -> bool:
    return financial_age_days(last_financials_date, as_of) > stale_days