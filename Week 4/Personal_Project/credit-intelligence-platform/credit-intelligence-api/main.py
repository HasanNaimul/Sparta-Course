from fastapi import FastAPI
from routers import borrowers, facilities, covenants, risk, insights

app = FastAPI(title="Credit Intelligence API", version="1.0.0")

app.include_router(borrowers.router)
app.include_router(facilities.router)
app.include_router(covenants.router)
app.include_router(risk.router)
app.include_router(insights.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "credit-intelligence-api"}