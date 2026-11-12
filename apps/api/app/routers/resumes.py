import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..models import Resume, CandidateFact, User
from ..security import get_current_user
from ..core.config import settings
from ..services.resume_parser import extract_text, propose_facts, ALLOWED

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("", status_code=201)
async def upload_resume(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED:
        raise HTTPException(415, "Upload a PDF or DOCX resume.")
    content = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if not content or len(content) > max_bytes:
        raise HTTPException(413, f"File must be between 1 byte and {settings.max_upload_mb} MB.")
    try:
        text = extract_text(content, file.content_type)
    except Exception:
        raise HTTPException(422, "Could not extract text from this file. Try a text-based PDF or DOCX.")
    if not text.strip():
        raise HTTPException(422, "No readable text found. Scanned PDFs require OCR, which is not enabled yet.")
    folder = Path(settings.upload_dir) / user.tenant_id
    folder.mkdir(parents=True, exist_ok=True)
    resume_id = str(uuid.uuid4())
    suffix = ALLOWED[file.content_type]
    storage_key = f"{user.tenant_id}/{resume_id}{suffix}"
    path = Path(settings.upload_dir) / storage_key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    row = Resume(id=resume_id, tenant_id=user.tenant_id,
                 original_filename=Path(file.filename or "resume").name[:255],
                 storage_key=storage_key, mime_type=file.content_type,
                 size_bytes=len(content), extracted_text=text)
    db.add(row)
    for item in propose_facts(text):
        exists = db.scalar(select(CandidateFact).where(
            CandidateFact.tenant_id == user.tenant_id,
            CandidateFact.fact_key == item["fact_key"],
            CandidateFact.fact_value == item["fact_value"]))
        if not exists:
            db.add(CandidateFact(tenant_id=user.tenant_id, resume_id=resume_id,
                                 fact_key=item["fact_key"], fact_value=item["fact_value"],
                                 confidence=item["confidence"], status="proposed"))
    db.commit()
    return {"resume_id": resume_id, "filename": row.original_filename,
            "parse_status": row.parse_status, "extracted_characters": len(text),
            "message": "Resume parsed. Extracted facts are proposals until you confirm them."}

@router.get("")
def list_resumes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Resume).where(Resume.tenant_id == user.tenant_id).order_by(Resume.created_at.desc()))
    return [{"id": r.id, "filename": r.original_filename, "parse_status": r.parse_status,
             "created_at": r.created_at, "size_bytes": r.size_bytes} for r in rows]
