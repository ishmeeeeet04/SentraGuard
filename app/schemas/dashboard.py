"""
Request/response shapes for the analyst dashboard endpoints.
"""

import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class TrafficItem(BaseModel):
    id: uuid.UUID
    prompt: str
    final_verdict: str
    llm_provider: str
    llm_model: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrafficListResponse(BaseModel):
    items: List[TrafficItem]
    total: int


class MetricsResponse(BaseModel):
    total_requests: int
    blocked_requests: int
    safe_requests: int
    block_rate_percent: float