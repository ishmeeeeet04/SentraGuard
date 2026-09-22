"""
The core gateway endpoint: receives a chat message from an authenticated
user, forwards it to the configured LLM provider, logs the full exchange,
and returns the response.

NOTE: This version has NO security detection yet — that's Module 3.
Right now this is pure plumbing: Auth -> LLM Provider -> Database Log.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.config import settings
from app.models.request_log import RequestLog
from app.models.user import User
from app.providers.factory import get_llm_provider
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1/proxy", tags=["proxy"])


@router.post("/chat", response_model=ChatResponse)
def proxy_chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    provider = get_llm_provider()
    reply_text = provider.chat(payload.message)

    log_entry = RequestLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        prompt=payload.message,
        response=reply_text,
        llm_provider="groq",
        llm_model=settings.groq_model,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return ChatResponse(request_id=log_entry.id, response=reply_text)