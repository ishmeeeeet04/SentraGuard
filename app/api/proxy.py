"""
The core gateway endpoint: receives a chat message from an authenticated
user, checks rate limits, runs it through the detection pipeline
(Module 3), and only forwards it to the LLM provider if allowed. Every
stage's verdict is logged to the database for the audit trail.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.config import settings
from app.core.rate_limiter import is_rate_limited
from app.detection.models import Verdict
from app.detection.pipeline import run_detection_pipeline
from app.models.detection_log import DetectionLog
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
    if is_rate_limited(str(current_user.id)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait before sending more requests.",
        )

    pipeline_state = run_detection_pipeline(payload.message)
    final_verdict = pipeline_state["final_verdict"]
    is_blocked = final_verdict == Verdict.BLOCK

    reply_text = None
    if not is_blocked:
        provider = get_llm_provider()
        reply_text = provider.chat(payload.message)

    log_entry = RequestLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        prompt=payload.message,
        response=reply_text,
        final_verdict=final_verdict.value,
        llm_provider="groq",
        llm_model=settings.groq_model,
    )
    db.add(log_entry)
    db.flush()

    for stage_result in pipeline_state["results"]:
        db.add(
            DetectionLog(
                request_id=log_entry.id,
                stage=stage_result.stage,
                verdict=stage_result.verdict.value,
                confidence=stage_result.confidence,
                reason=stage_result.reason,
            )
        )

    db.commit()
    db.refresh(log_entry)

    if is_blocked:
        blocking_stage = pipeline_state["results"][-1]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Request blocked by {blocking_stage.stage}: {blocking_stage.reason}",
        )

    return ChatResponse(request_id=log_entry.id, response=reply_text)