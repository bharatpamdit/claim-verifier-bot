
from fastapi import FastAPI

app = FastAPI(
    title="Claim Verifier Bot",
    description="Evidence-based GitHub Issue and PR verification",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Claim Verifier Bot Backend is Running!"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
