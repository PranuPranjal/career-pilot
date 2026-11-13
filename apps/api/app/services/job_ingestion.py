import hashlib
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..models import JobSource, JobPosting
from .job_sources import ADAPTERS


def sync_source(db: Session, source: JobSource) -> dict:
    adapter = ADAPTERS.get(source.provider)
    if not adapter:
        raise ValueError("Unsupported provider")
    try:
        fetched = adapter.fetch(source.board_token)
        now = datetime.now(timezone.utc)
        seen_ids = set()
        created = updated = 0
        for job in fetched:
            seen_ids.add(job.external_id)
            source_name = source.company_name
            company = job.company_name or source_name
            raw_hash = "|".join([job.title, company, job.location, job.description_text, job.job_url])
            digest = hashlib.sha256(raw_hash.encode("utf-8")).hexdigest()
            existing = db.scalar(select(JobPosting).where(JobPosting.source_id == source.id, JobPosting.external_id == job.external_id))
            values = dict(title=job.title, company_name=company, location=job.location or "", department=job.department or "",
                employment_type=job.employment_type or "", workplace_type=job.workplace_type or "",
                description_text=job.description_text or "", description_html=job.description_html or "",
                job_url=job.job_url, apply_url=job.apply_url or job.job_url, published_at=job.published_at,
                source_updated_at=job.source_updated_at, content_hash=digest, status="active", last_seen_at=now)
            if existing:
                for key, value in values.items():
                    setattr(existing, key, value)
                updated += 1
            else:
                db.add(JobPosting(source_id=source.id, external_id=job.external_id, first_seen_at=now, **values))
                created += 1
        db.flush()
        old_jobs = db.scalars(select(JobPosting).where(JobPosting.source_id == source.id, JobPosting.status == "active")).all()
        stale = 0
        if fetched:
            for old in old_jobs:
                if old.external_id not in seen_ids:
                    old.status = "stale"
                    stale += 1
        source.last_sync_at = now
        source.last_sync_status = "success"
        source.last_sync_error = None
        db.commit()
        return {"source_id": source.id, "fetched": len(fetched), "created": created, "updated": updated, "marked_stale": stale}
    except Exception as exc:
        db.rollback()
        source = db.get(JobSource, source.id)
        if source:
            source.last_sync_at = datetime.now(timezone.utc)
            source.last_sync_status = "failed"
            source.last_sync_error = str(exc)[:1000]
            db.commit()
        raise
