from fastapi import FastAPI


app = FastAPI(
    title="Credit Intelligence API",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "credit-intelligence-api",
    }