from fastapi import FastAPI
from routers import firms, people, reports, knowledge, agent
from routers.insights import router as insights_router


app = FastAPI(title="Firm Intelligence API")


app.include_router(firms.router)
app.include_router(people.router)
app.include_router(reports.router)
app.include_router(insights_router)
app.include_router(knowledge.router)
app.include_router(agent.router)


@app.get("/health")
def health():
    return {"status": "ok"}