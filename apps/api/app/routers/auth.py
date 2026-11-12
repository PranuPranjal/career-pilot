from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..models import Tenant, User, CandidateProfile
from ..schemas import RegisterIn, LoginIn, TokenOut
from ..security import hash_password, verify_password, create_access_token, get_current_user
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "An account with this email already exists.")
    tenant = Tenant(name=payload.workspace_name.strip())
    db.add(tenant)
    db.flush()
    user = User(tenant_id=tenant.id, email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.add(CandidateProfile(tenant_id=tenant.id))
    db.commit()
    return TokenOut(access_token=create_access_token(user), expires_in=settings.access_token_minutes * 60)

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password.")
    if not user.is_active:
        raise HTTPException(403, "This account is disabled.")
    return TokenOut(access_token=create_access_token(user), expires_in=settings.access_token_minutes * 60)

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"user_id": user.id, "tenant_id": user.tenant_id, "email": user.email}
