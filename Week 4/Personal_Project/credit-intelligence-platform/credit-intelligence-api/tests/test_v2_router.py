from fastapi.testclient import TestClient

from main import app
from v2 import router as v2_router

client = TestClient(app)


def test_v2_ask_returns_grounded_answer(monkeypatch):
    monkeypatch.setattr(
        v2_router.graph,
        "invoke",
        lambda state: {
            "messages": [
                type("Message", (), {"content": "COV-4201 requires net leverage not to exceed 4.5x [credit-doc-013]."})()
            ]
        },
    )

    response = client.post("/v2/knowledge/ask", json={"question": "What does COV-4201 require?"})

    assert response.status_code == 200
    assert response.json()["refused"] is False
    assert "4.5x" in response.json()["answer"]


def test_v2_ask_returns_refusal(monkeypatch):
    monkeypatch.setattr(
        v2_router.graph,
        "invoke",
        lambda state: {
            "messages": [
                type("Message", (), {"content": "The provided documents do not answer that question."})()
            ]
        },
    )

    response = client.post("/v2/knowledge/ask", json={"question": "Who is Redwood Healthcare's external auditor?"})

    assert response.status_code == 200
    assert response.json()["refused"] is True
    assert response.json()["answer"] is None