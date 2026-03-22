from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from app.database import get_db
from app.models import User, InterviewSession, Message, SessionStatus
from app.schemas import StartInterviewRequest, InterviewResponse, UserAnswerRequest, SessionOut
from app.auth import get_current_user
from app.llm_client import llm_client
from app.prompts import get_system_prompt, build_feedback_prompt

router = APIRouter(prefix="/interview", tags=["Interview"])


def _build_messages(system_prompt: str, db_messages: list[Message]) -> list[dict]:
    """Convert DB messages into LLM-compatible message list."""
    messages = [{"role": "system", "content": system_prompt}]
    for m in db_messages:
        messages.append({"role": m.role, "content": m.content})
    return messages


@router.post("/start", response_model=InterviewResponse)
async def start_interview(
    payload: StartInterviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create session
    session = InterviewSession(
        user_id=current_user.id,
        interview_type=payload.interview_type,
        status=SessionStatus.active
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Ask LLM to open the interview
    system_prompt = get_system_prompt(payload.interview_type.value)
    system_prompt += "\n\nCRITICAL: Never answer your own questions or provide answers to the candidate. If their response is vague, ask them to elaborate."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Start the interview. Greet me and ask your first question."}
    ]

    first_question = await llm_client.chat(messages)

    # Save opening message
    msg = Message(session_id=session.id, role="assistant", content=first_question)
    db.add(msg)
    await db.commit()

    return {"session_id": session.id, "message": first_question}


@router.post("/respond", response_model=InterviewResponse)
async def respond(
    payload: UserAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.messages))
        .where(
            InterviewSession.id == payload.session_id,
            InterviewSession.user_id == current_user.id,
            InterviewSession.status == SessionStatus.active
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")

    # Save user's answer
    user_msg = Message(session_id=session.id, role="user", content=payload.answer)
    db.add(user_msg)
    await db.commit()

    # Reload messages including the new user message
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.messages))
        .where(InterviewSession.id == session.id)
    )
    session = result.scalar_one()

    # Build full conversation context and get AI reply
    system_prompt = get_system_prompt(session.interview_type.value)
    system_prompt += "\n\nCRITICAL: If the candidate gives a wrong or incomplete answer, correct them clearly and explain the right answer briefly. If their response is too vague or off-topic, ask them to elaborate. Never answer a question the candidate hasn't attempted yet."
    messages = _build_messages(system_prompt, session.messages)
    ai_reply = await llm_client.chat(messages)
    
    # Guard against empty LLM response
    if not ai_reply or not ai_reply.strip():
        import logging
        logging.getLogger(__name__).warning("LLM returned empty response for session %s", session.id)
        ai_reply = "I didn't quite catch that. Could you elaborate a bit more?"

    # Save AI reply
    ai_msg = Message(session_id=session.id, role="assistant", content=ai_reply)
    db.add(ai_msg)
    await db.commit()

    return {"session_id": session.id, "message": ai_reply}


@router.post("/end/{session_id}", response_model=SessionOut)
async def end_interview(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.messages))
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Generate feedback report via LLM
    feedback_prompt = build_feedback_prompt(session.interview_type.value, session.messages)
    feedback_messages = [{"role": "user", "content": feedback_prompt}]
    raw_feedback = await llm_client.chat(feedback_messages, max_tokens=1024)

    # Parse score from feedback (looks for "SCORE: 75")
    score = 0
    for line in raw_feedback.splitlines():
        if line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip())
            except ValueError:
                pass
            break

    session.status = SessionStatus.completed
    session.ended_at = datetime.utcnow()
    session.feedback = raw_feedback
    session.score = score
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions", response_model=list[SessionOut])
async def get_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.messages))
        .where(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.created_at.desc())
    )
    return result.scalars().all()


@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.messages))
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
