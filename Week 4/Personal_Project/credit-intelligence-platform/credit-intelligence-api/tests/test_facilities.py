from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_list_facilities():
    response = client.get("/facilities")

    assert response.status_code == 200
    assert len(response.json()) == 6


def test_filter_facilities_by_borrower():
    response = client.get("/facilities",params={"borrower_id": 1},)

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 1
    assert results[0]["borrower_id"] == 1


def test_filter_secured_facilities():
    response = client.get(
        "/facilities",
        params={"secured": True},
    )

    assert response.status_code == 200

    assert all(
        facility["secured"] is True
        for facility in response.json()
    )


def test_create_facility():
    facility = {
        "borrower_id": 1,
        "facility_type": "term_loan",
        "currency": "GBP",
        "committed_amount_m": 50.0,
        "drawn_amount_m": 40.0,
        "margin_bps": 200,
        "maturity_date": "2030-06-30",
        "secured": False,
    }

    response = client.post(
        "/facilities",
        json=facility,
    )

    assert response.status_code == 201
    assert response.json()["id"] == 7


def test_facility_rejects_unknown_borrower():
    facility = {
        "borrower_id": 999,
        "facility_type": "term_loan",
        "currency": "GBP",
        "committed_amount_m": 50.0,
        "drawn_amount_m": 40.0,
        "margin_bps": 200,
        "maturity_date": "2030-06-30",
        "secured": False,
    }

    response = client.post(
        "/facilities",
        json=facility,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Borrower not found"


def test_delete_facility():
    response = client.delete("/facilities/6")

    assert response.status_code == 204

    check = client.get("/facilities/6")

    assert check.status_code == 404