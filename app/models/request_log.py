"""
Request log model — records every prompt/response pair that passes
through the gateway. This is the foundation for the audit trail and
the analyst dashboard's live traffic feed.
"""

import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)  # nullable: a blocked request may have no LLM response
    final_verdict = Column(String(20), nullable=False, default="safe")

    llm_provider = Column(String(50), nullable=False)
    llm_model = Column(String(100), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())