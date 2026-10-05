from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_facilities():
    response = client.get("/facilities")
    assert response.status_code == 200
    assert len(response.json()) == 6


def test_get_facility():
    response = client.get("/facilities/1")
    assert response.status_code == 200
    assert response.json()["borrower_id"] == 1


def test_unknown_facility():
    response = client.get("/facilities/999")
    assert response.status_code == 404


def test_borrower_filter():
    response = client.get("/facilities", params={"borrower_id": 1})
    assert response.status_code == 200
    assert all(f["borrower_id"] == 1 for f in response.json())


def test_secured_filter():
    response = client.get("/facilities", params={"secured": True})
    assert response.status_code == 200
    assert all(f["secured"] is True for f in response.json())


def test_create_facility():
    new = {
        "borrower_id": 1,
        "facility_type": "term_loan",
        "currency": "GBP",
        "committed_amount_m": 50.0,
        "drawn_amount_m": 40.0,
        "margin_bps": 200,
        "maturity_date": "2030-06-30",
        "secured": False,
    }

    response = client.post("/facilities", json=new)
    assert response.status_code == 201
    assert response.json()["id"] == 7


def test_unknown_borrower_rejected():
    new = {
        "borrower_id": 999,
        "facility_type": "term_loan",
        "currency": "GBP",
        "committed_amount_m": 50.0,
        "drawn_amount_m": 40.0,
        "margin_bps": 200,
        "maturity_date": "2030-06-30",
        "secured": False,
    }

    response = client.post("/facilities", json=new)
    assert response.status_code == 404
    assert response.json()["detail"] == "Borrower not found"


def test_delete_facility():
    response = client.delete("/facilities/6")
    assert response.status_code == 204
    assert client.get("/facilities/6").status_code == 404