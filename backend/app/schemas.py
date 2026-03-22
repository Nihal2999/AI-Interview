from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models import InterviewType, SessionStatus


# ── Auth ──────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Interview ─────────────────────────────────────────

class StartInterviewRequest(BaseModel):
    interview_type: InterviewType

class InterviewResponse(BaseModel):
    session_id: int
    message: str               # AI's question/response

class UserAnswerRequest(BaseModel):
    session_id: int
    answer: str

class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}

class SessionOut(BaseModel):
    id: int
    interview_type: InterviewType
    status: SessionStatus
    score: int | None
    feedback: str | None
    created_at: datetime
    ended_at: datetime | None
    messages: list[MessageOut] = []

    model_config = {"from_attributes": True}
