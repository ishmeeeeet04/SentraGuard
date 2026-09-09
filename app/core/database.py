"""
Database engine and session management.
Every other file that needs to talk to Postgres imports from here.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

DATABASE_URL = (
    f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}"
    f"@localhost:{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency — gives each request its own database session,
    and always closes it afterwards, even if an error happens.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        