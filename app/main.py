"""
Application entry point.
This is the file uvicorn loads to start the server.
"""

from fastapi import FastAPI, Depends

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.deps import get_current_user, require_role
from app.models.user import User
from app.schemas.user import UserOut

app = FastAPI(
    title="SentraGuard",
    description="AI Security Gateway for Prompt Injection Detection & Sensitive Data Leak Prevention",
    version="0.1.0",
)

app.include_router(auth_router)


@app.get("/")
def root():
    """Simple root endpoint — confirms the server is alive."""
    return {"message": "SentraGuard is running", "status": "ok"}


@app.get("/health")
def health():
    """
    Health check endpoint. Right now it just confirms the app loaded its
    settings correctly. Later, this will also check the database connection.
    """
    return {
        "status": "healthy",
        "postgres_db": settings.postgres_db,
        "redis_port": settings.redis_port,
    }


@app.get("/api/v1/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Any logged-in user can call this — returns their own profile."""
    return current_user


@app.get("/api/v1/admin/ping")
def admin_only_ping(current_user: User = Depends(require_role("admin"))):
    """Only users with role='admin' can call this — demonstrates RBAC."""
    return {"message": f"Hello Admin {current_user.email}, you have admin access."}