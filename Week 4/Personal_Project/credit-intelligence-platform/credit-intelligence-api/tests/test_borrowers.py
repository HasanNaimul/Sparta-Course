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


def test_unknown_borrower():
    response = client.get("/borrowers/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Borrower not found"


def test_sector_filter():
    response = client.get("/borrowers", params={"sector": "Manufacturing"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_watchlist_filter():
    response = client.get("/borrowers", params={"watchlist": True})
    assert response.status_code == 200
    assert all(b["watchlist"] is True for b in response.json())


def test_create_borrower():
    new = {
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

    response = client.post("/borrowers", json=new)
    assert response.status_code == 201
    assert response.json()["id"] == 7


def test_invalid_borrower():
    new = {
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

    response = client.post("/borrowers", json=new)
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

    response = client.put("/borrowers/1", json=updated)
    assert response.status_code == 200
    assert response.json()["internal_risk_band"] == "elevated"
    assert response.json()["watchlist"] is True


def test_delete_borrower():
    response = client.delete("/borrowers/6")
    assert response.status_code == 204
    assert client.get("/borrowers/6").status_code == 404