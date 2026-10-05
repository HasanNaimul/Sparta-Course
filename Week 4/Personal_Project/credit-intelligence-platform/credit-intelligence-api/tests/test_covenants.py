from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_covenants():
    response = client.get("/covenants")
    assert response.status_code == 200
    assert len(response.json()) == 11


def test_get_covenant():
    response = client.get("/covenants/1")
    assert response.status_code == 200
    assert response.json()["facility_id"] == 1


def test_unknown_covenant():
    response = client.get("/covenants/999")
    assert response.status_code == 404


def test_facility_filter():
    response = client.get("/covenants", params={"facility_id": 1})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_metric_filter():
    response = client.get("/covenants", params={"metric": "net_leverage"})
    assert response.status_code == 200
    assert all(c["metric"] == "net_leverage" for c in response.json())


def test_create_covenant():
    new = {
        "facility_id": 4,
        "metric": "interest_cover",
        "threshold": 2.5,
        "comparison": "minimum",
        "testing_frequency": "semi_annual",
        "last_test_date": "2026-06-30",
    }

    response = client.post("/covenants", json=new)
    assert response.status_code == 201
    assert response.json()["id"] == 12


def test_unknown_facility_rejected():
    new = {
        "facility_id": 999,
        "metric": "net_leverage",
        "threshold": 4.0,
        "comparison": "maximum",
        "testing_frequency": "quarterly",
        "last_test_date": "2026-06-30",
    }

    response = client.post("/covenants", json=new)
    assert response.status_code == 404
    assert response.json()["detail"] == "Facility not found"


def test_delete_covenant():
    response = client.delete("/covenants/11")
    assert response.status_code == 204
    assert client.get("/covenants/11").status_code == 404