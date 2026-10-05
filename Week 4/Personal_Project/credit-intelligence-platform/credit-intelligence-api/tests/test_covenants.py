from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_list_covenants():
    response = client.get("/covenants")

    assert response.status_code == 200
    assert len(response.json()) == 11


def test_filter_covenants_by_facility():
    response = client.get(
        "/covenants",
        params={"facility_id": 1},
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 2
    assert all(
        covenant["facility_id"] == 1
        for covenant in results
    )


def test_filter_by_metric():
    response = client.get(
        "/covenants",
        params={"metric": "net_leverage"},
    )

    assert response.status_code == 200

    assert all(
        covenant["metric"] == "net_leverage"
        for covenant in response.json()
    )


def test_create_covenant():
    covenant = {
        "facility_id": 4,
        "metric": "interest_cover",
        "threshold": 2.5,
        "comparison": "minimum",
        "testing_frequency": "semi_annual",
        "last_test_date": "2026-06-30",
    }

    response = client.post(
        "/covenants",
        json=covenant,
    )

    assert response.status_code == 201
    assert response.json()["id"] == 12


def test_covenant_rejects_unknown_facility():
    covenant = {
        "facility_id": 999,
        "metric": "net_leverage",
        "threshold": 4.0,
        "comparison": "maximum",
        "testing_frequency": "quarterly",
        "last_test_date": "2026-06-30",
    }

    response = client.post(
        "/covenants",
        json=covenant,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Facility not found"


def test_unknown_covenant_returns_404():
    response = client.get("/covenants/999")

    assert response.status_code == 404