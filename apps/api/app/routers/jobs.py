import re
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session, joinedload
from ..db import get_db
from ..models import JobSource, JobPosting, User
from ..security import get_current_user
from ..services.job_ingestion import sync_source

router = APIRouter(tags=["Job discovery"])

class SourceCreate(BaseModel):
    provider: str = Field(pattern="^(greenhouse|lever|ashby)$")
    company_name: str = Field(min_length=2, max_length=200)
    board_token: str = Field(min_length=1, max_length=300)

@router.get("/sources")
def list_sources(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sources = db.scalars(select(JobSource).order_by(JobSource.company_name)).all()
    return [{"id": s.id, "provider": s.provider, "company_name": s.company_name, "board_token": s.board_token,
             "is_enabled": s.is_enabled, "last_sync_at": s.last_sync_at, "last_sync_status": s.last_sync_status,
             "last_sync_error": s.last_sync_error} for s in sources]

@router.post("/sources", status_code=201)
def create_source(payload: SourceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    token = payload.board_token.strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", token):
        raise HTTPException(422, "Board token can contain only letters, numbers, dots, underscores and hyphens.")
    existing = db.scalar(select(JobSource).where(JobSource.provider == payload.provider, JobSource.board_token == token))
    if existing:
        return {"id": existing.id, "provider": existing.provider, "company_name": existing.company_name, "already_exists": True}
    source = JobSource(provider=payload.provider, company_name=payload.company_name.strip(), board_token=token)
    db.add(source)
    db.commit()
    db.refresh(source)
    return {"id": source.id, "provider": source.provider, "company_name": source.company_name, "already_exists": False}

@router.post("/sources/{source_id}/sync")
def sync_job_source(source_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    source = db.get(JobSource, source_id)
    if not source:
        raise HTTPException(404, "Job source not found.")
    if not source.is_enabled:
        raise HTTPException(409, "This source is disabled.")
    try:
        return sync_source(db, source)
    except Exception as exc:
        raise HTTPException(502, f"Source sync failed: {str(exc)[:300]}")

@router.get("/jobs")
def list_jobs(
    q: str | None = Query(default=None, max_length=150),
    location: str | None = Query(default=None, max_length=150),
    provider: str | None = Query(default=None, pattern="^(greenhouse|lever|ashby)$"),
    employment_type: str | None = Query(default=None, max_length=80),
    workplace_type: str | None = Query(default=None, max_length=40),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    include_stale: bool = False,
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    stmt = select(JobPosting).options(joinedload(JobPosting.source))
    filters = []
    if not include_stale:
        filters.append(JobPosting.status == "active")
    if q:
        term = f"%{q.strip()}%"
        filters.append(or_(JobPosting.title.ilike(term), JobPosting.company_name.ilike(term), JobPosting.description_text.ilike(term), JobPosting.department.ilike(term)))
    if location:
        filters.append(JobPosting.location.ilike(f"%{location.strip()}%"))
    if provider:
        stmt = stmt.join(JobSource, JobPosting.source_id == JobSource.id)
        filters.append(JobSource.provider == provider)
    if employment_type:
        filters.append(JobPosting.employment_type.ilike(f"%{employment_type}%"))
    if workplace_type:
        filters.append(JobPosting.workplace_type.ilike(f"%{workplace_type}%"))
    if filters:
        stmt = stmt.where(*filters)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0
    rows = db.scalars(stmt.order_by(JobPosting.published_at.desc().nullslast(), JobPosting.first_seen_at.desc()).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return {"items": [serialize_job(j) for j in rows], "total": total, "page": page, "page_size": page_size, "pages": (total + page_size - 1) // page_size}

@router.get("/jobs/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = db.scalar(select(JobPosting).options(joinedload(JobPosting.source)).where(JobPosting.id == job_id))
    if not job:
        raise HTTPException(404, "Job not found.")
    return serialize_job(job, include_description=True)


def serialize_job(job: JobPosting, include_description: bool = False):
    result = {"id": job.id, "external_id": job.external_id, "title": job.title, "company_name": job.company_name,
        "location": job.location, "department": job.department, "employment_type": job.employment_type,
        "workplace_type": job.workplace_type, "job_url": job.job_url, "apply_url": job.apply_url,
        "published_at": job.published_at, "status": job.status, "provider": job.source.provider if job.source else "",
        "first_seen_at": job.first_seen_at, "last_seen_at": job.last_seen_at}
    if include_description:
        result["description_text"] = job.description_text
        result["description_html"] = job.description_html
    return result
