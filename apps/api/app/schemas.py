from pydantic import BaseModel, EmailStr, Field
from typing import Any

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    workspace_name: str = Field(min_length=1, max_length=200)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class ProfileUpdate(BaseModel):
    display_name: str = ""
    headline: str = ""
    location: str = ""
    experience_summary: str = ""
    skills: list[str] = []
    preferences: dict[str, Any] = {}

class FactUpdate(BaseModel):
    status: str = Field(pattern="^(confirmed|rejected)$")
    corrected_value: str | None = None

class OnboardingMessageIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
