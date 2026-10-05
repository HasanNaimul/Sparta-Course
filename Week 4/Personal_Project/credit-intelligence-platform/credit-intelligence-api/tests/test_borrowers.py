from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_list_borrowers():
    response = client.get("/borrowers")

    assert response.status_code == 200
    assert len(response.json()) == 6


def test_get_borrower():
    response = client.get("/borrowers/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Northbridge Components Ltd"


def test_unknown_borrower_returns_404():
    response = client.get("/borrowers/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Borrower not found"


def test_filter_borrowers_by_sector():
    response = client.get(
        "/borrowers",
        params={"sector": "Manufacturing"},
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 1
    assert results[0]["name"] == "Northbridge Components Ltd"


def test_filter_watchlist_borrowers():
    response = client.get(
        "/borrowers",
        params={"watchlist": True},
    )

    assert response.status_code == 200

    results = response.json()

    assert all(
        borrower["watchlist"] is True
        for borrower in results
    )


def test_create_borrower():
    new_borrower = {
        "name": "Silverstone Foods Ltd",
        "sector": "Food Manufacturing",
        "country": "United Kingdom",
        "internal_risk_band": "moderate",
        "revenue_m": 350.0,
        "ebitda_m": 55.0,
        "total_debt_m": 140.0,
        "cash_m": 25.0,
        "interest_expense_m": 12.0,
        "last_financials_date": "2026-09-30",
        "watchlist": False,
    }

    response = client.post(
        "/borrowers",
        json=new_borrower,
    )

    assert response.status_code == 201
    assert response.json()["id"] == 7
    assert response.json()["name"] == "Silverstone Foods Ltd"


def test_invalid_borrower_is_rejected():
    invalid_borrower = {
        "name": "Bad Data Ltd",
        "sector": "Retail",
        "country": "United Kingdom",
        "internal_risk_band": "moderate",
        "revenue_m": -100,
        "ebitda_m": 50,
        "total_debt_m": 100,
        "cash_m": 10,
        "interest_expense_m": 10,
        "last_financials_date": "2026-09-30",
        "watchlist": False,
    }

    response = client.post(
        "/borrowers",
        json=invalid_borrower,
    )

    assert response.status_code == 422


def test_update_borrower():
    updated = {
        "name": "Northbridge Components Ltd",
        "sector": "Manufacturing",
        "country": "United Kingdom",
        "internal_risk_band": "elevated",
        "revenue_m": 520.0,
        "ebitda_m": 82.0,
        "total_debt_m": 245.0,
        "cash_m": 38.0,
        "interest_expense_m": 24.0,
        "last_financials_date": "2026-08-31",
        "watchlist": True,
    }

    response = client.put(
        "/borrowers/1",
        json=updated,
    )

    assert response.status_code == 200
    assert response.json()["internal_risk_band"] == "elevated"
    assert response.json()["watchlist"] is True


def test_delete_borrower():
    response = client.delete("/borrowers/6")

    assert response.status_code == 204

    check = client.get("/borrowers/6")

    assert check.status_code == 404