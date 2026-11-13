from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routers import auth, profile, resumes, onboarding, jobs

app = FastAPI(title="CareerPilot API", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(profile.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(onboarding.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "service": "careerpilot-api"}
