from fastapi.testclient import TestClient

from main import app
from v2 import router as v2_router

client = TestClient(app)


def test_v2_ask_returns_grounded_answer(monkeypatch):
    monkeypatch.setattr(
        v2_router.graph,
        "invoke",
        lambda state, config=None: {
            "messages": [
                type(
                    "Message",
                    (),
                    {"content": "COV-4201 requires net leverage not to exceed 4.5x [credit-doc-013]."},
                )()
            ]
        },
    )

    response = client.post(
        "/v2/knowledge/ask",
        json={"question": "What does COV-4201 require?"},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["refused"] is False
    assert "4.5x" in body["answer"]
    assert body["thread_id"]


def test_v2_ask_returns_refusal(monkeypatch):
    monkeypatch.setattr(
        v2_router.graph,
        "invoke",
        lambda state, config=None: {
            "messages": [
                type(
                    "Message",
                    (),
                    {"content": "The provided documents do not answer that question."},
                )()
            ]
        },
    )

    response = client.post(
        "/v2/knowledge/ask",
        json={"question": "Who is Redwood Healthcare's external auditor?"},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["refused"] is True
    assert body["answer"] is None
    assert body["thread_id"]


def test_v2_ask_reuses_thread_id(monkeypatch):
    captured = {}

    def fake_invoke(state, config=None):
        captured["config"] = config
        return {
            "messages": [
                type("Message", (), {"content": "FAC-3115 matures on 31 December 2028."})()
            ]
        }

    monkeypatch.setattr(v2_router.graph, "invoke", fake_invoke)

    response = client.post(
        "/v2/knowledge/ask",
        json={
            "question": "When does it mature?",
            "thread_id": "credit-thread-1",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["thread_id"] == "credit-thread-1"
    assert captured["config"]["configurable"]["thread_id"] == "credit-thread-1"