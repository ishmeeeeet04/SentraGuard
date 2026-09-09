"""
Response shape for user data. Notice password_hash is never included here —
this is what gets sent back to the client, never the raw database row.
"""

import uuid

from pydantic import BaseModel, EmailStr, ConfigDict


class UserOut(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)