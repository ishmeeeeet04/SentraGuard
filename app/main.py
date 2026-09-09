"""
Application entry point.
This is the file uvicorn loads to start the server.
"""

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title="SentraGuard",
    description="AI Security Gateway for Prompt Injection Detection & Sensitive Data Leak Prevention",
    version="0.1.0",
)


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