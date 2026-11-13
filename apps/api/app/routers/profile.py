from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..models import CandidateProfile, CandidateFact, User
from ..schemas import ProfileUpdate, FactUpdate
from ..security import get_current_user

router = APIRouter(prefix="/profile", tags=["Candidate profile"])

@router.get("")
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.tenant_id == user.tenant_id))
    if not profile: raise HTTPException(404, "Profile not found.")
    return profile

@router.put("")
def update_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.tenant_id == user.tenant_id))
    if not profile: raise HTTPException(404, "Profile not found.")
    for key, value in payload.model_dump().items():
        setattr(profile, key, value)
    db.commit(); db.refresh(profile)
    return profile

@router.get("/facts")
def list_facts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list(db.scalars(select(CandidateFact).where(CandidateFact.tenant_id == user.tenant_id).order_by(CandidateFact.created_at.desc())))

@router.post("/facts/{fact_id}/confirm")
def update_fact(fact_id: str, payload: FactUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fact = db.scalar(select(CandidateFact).where(CandidateFact.id == fact_id, CandidateFact.tenant_id == user.tenant_id))
    if not fact: raise HTTPException(404, "Fact not found.")
    fact.status = payload.status
    if payload.corrected_value is not None:
        fact.fact_value = payload.corrected_value.strip()
    db.commit(); db.refresh(fact)
    return fact
