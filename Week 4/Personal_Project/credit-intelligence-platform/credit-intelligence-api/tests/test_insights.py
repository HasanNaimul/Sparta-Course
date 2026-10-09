from fastapi.testclient import TestClient
from models import CreditAssessment
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


def test_borrower_analysis(monkeypatch):
    fake_analysis = CreditAssessment(
        risk_level="moderate",
        strengths=["Positive EBITDA", "Adequate interest cover"],
        risks=["Meaningful debt burden"],
        covenant_status="comfortable",
        outlook="stable",
        recommended_action="maintain",
        rationale="Current metrics indicate manageable leverage and adequate debt service capacity.",
    )

    fake_result = {"analysis": fake_analysis, "input_tokens": 250, "output_tokens": 90, "stop_reason": "end_turn"}
    monkeypatch.setattr(llm, "analyse_borrower", lambda borrower, metrics: fake_result)

    response = client.get("/borrowers/1/analysis")
    body = response.json()

    assert response.status_code == 200
    assert body["borrower_id"] == 1
    assert body["analysis"]["risk_level"] == "moderate"
    assert body["analysis"]["covenant_status"] == "comfortable"
    assert body["analysis"]["recommended_action"] == "maintain"
    assert body["input_tokens"] == 250