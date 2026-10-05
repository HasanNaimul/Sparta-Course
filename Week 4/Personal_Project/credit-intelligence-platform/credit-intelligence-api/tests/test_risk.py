from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_northbridge_stress_test():
    response = client.post("/borrowers/1/stress-test", json={"ebitda_shock_pct": -20})
    assert response.status_code == 200

    body = response.json()
    assert body["metrics"]["stressed_net_leverage"] == 3.16
    assert all(c["stressed_status"] != "breached" for c in body["covenants"])


def test_asteron_breaches_under_stress():
    response = client.post("/borrowers/3/stress-test", json={"ebitda_shock_pct": -20})
    assert response.status_code == 200

    body = response.json()
    assert body["metrics"]["stressed_net_leverage"] == 4.95
    assert any(c["stressed_status"] == "breached" for c in body["covenants"])


def test_unknown_borrower_returns_404():
    response = client.post("/borrowers/999/stress-test", json={"ebitda_shock_pct": -20})
    assert response.status_code == 404


def test_positive_stress_is_rejected():
    response = client.post("/borrowers/1/stress-test", json={"ebitda_shock_pct": 20})
    assert response.status_code == 422