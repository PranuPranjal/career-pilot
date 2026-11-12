from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..db import get_db
from ..models import User, CandidateProfile, CandidateFact, OnboardingMessage
from ..schemas import OnboardingMessageIn
from ..security import get_current_user

router = APIRouter(prefix="/onboarding", tags=["Conversational onboarding"])

QUESTIONS = [
    ("display_name", "What name would you like employers to see?"),
    ("location", "Which city or location are you currently based in, and are you open to relocation?"),
    ("target_roles", "Which job titles or role types are you targeting?"),
    ("experience_summary", "Could you briefly describe your work experience, internships or relevant projects?"),
]

@router.post("/messages")
def send_message(payload: OnboardingMessageIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(OnboardingMessage(tenant_id=user.tenant_id, role="user", content=payload.message))
    profile = db.scalar(select(CandidateProfile).where(CandidateProfile.tenant_id == user.tenant_id))
    missing = []
    if not profile.display_name: missing.append(QUESTIONS[0][1])
    if not profile.location: missing.append(QUESTIONS[1][1])
    if not profile.preferences.get("target_roles"): missing.append(QUESTIONS[2][1])
    if not profile.experience_summary: missing.append(QUESTIONS[3][1])
    if missing:
        reply = "Thanks. I’ll use your answer as context, but I won’t treat it as a verified profile fact until it is saved and confirmed. To complete your profile: " + missing[0]
    else:
        reply = "Your basic profile is complete. Review your extracted resume facts and confirm or correct each one before we use it in tailored application documents."
    db.add(OnboardingMessage(tenant_id=user.tenant_id, role="assistant", content=reply))
    db.commit()
    return {"reply": reply, "mode": "deterministic_onboarding_stub",
            "note": "LLM-based conversational extraction will be added after privacy and provider review."}
