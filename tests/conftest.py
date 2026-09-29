"""
Shared pytest fixtures for integration tests.
Uses a SEPARATE test database (sentraguard_test) so tests never touch
your real development data. pytest automatically discovers fixtures
defined here and makes them available to every test file.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.database import Base, get_db
import app.models  # noqa: F401  registers all models with Base.metadata
from app.main import app

TEST_DATABASE_URL = (
    f"postgresql+psycopg2://{settings.postgres_user}:{settings.postgres_password}"
    f"@localhost:{settings.postgres_port}/sentraguard_test"
)

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Runs ONCE per test session: wipes and recreates all tables fresh."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """A fresh database session, handed to each individual test."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """
    A FastAPI TestClient wired to use the TEST database instead of the
    real one — this is what lets us call actual API endpoints in tests
    without touching real data.
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()