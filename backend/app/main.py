from fastapi import FastAPI

app = FastAPI(
    title="AI Recruitment ATS",
    description="AI-assisted recruitment and CV screening API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the basic health status of the API."""
    return {"status": "ok"}
