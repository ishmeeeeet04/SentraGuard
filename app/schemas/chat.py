"""
Request/response shapes for the /proxy/chat endpoint.
"""

import uuid

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    request_id: uuid.UUID
    response: str