"""
Request/response shapes for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    org_name: str
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"