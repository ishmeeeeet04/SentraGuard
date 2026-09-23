"""
Detection log model — records the verdict of EVERY pipeline stage that
ran for a given request. This is the audit trail: an analyst can look
at one request and see exactly which stage flagged what, and why.
"""

import uuid

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class DetectionLog(Base):
    __tablename__ = "detection_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("request_logs.id", ondelete="CASCADE"), nullable=False)

    stage = Column(String(50), nullable=False)
    verdict = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    reason = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())