from fastapi.testclient import TestClient

import llm
from main import app

client = TestClient(app)


def test_borrower_summary(monkeypatch):
    fake_result = {"summary": "Northbridge remains moderately leveraged.", "input_tokens": 120, "output_tokens": 35, "stop_reason": "end_turn"}

    monkeypatch.setattr(llm, "summarise_borrower", lambda borrower, metrics: fake_result)

    response = client.get("/borrowers/1/summary")
    body = response.json()

    assert response.status_code == 200
    assert body["borrower_id"] == 1
    assert body["borrower_name"] == "Northbridge Components Ltd"
    assert body["summary"] == "Northbridge remains moderately leveraged."
    assert body["input_tokens"] == 120


def test_borrower_summary_stream(monkeypatch):
    def fake_stream(borrower, metrics):
        yield "Northbridge remains "
        yield "moderately leveraged."

    monkeypatch.setattr(llm, "stream_borrower_summary", fake_stream)

    response = client.get("/borrowers/1/summary/stream")

    assert response.status_code == 200
    assert response.text == "Northbridge remains moderately leveraged."