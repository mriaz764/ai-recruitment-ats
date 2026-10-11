from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.modules.jobs.router import router as jobs_router

app = FastAPI(
    title="AI Recruitment ATS",
    description="AI-assisted recruitment and CV screening API",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(jobs_router)
