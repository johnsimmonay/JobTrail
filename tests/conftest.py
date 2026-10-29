# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.main import app
from app.models import Base
from app.config import DATABASE_TEST_URL


test_engine = create_engine(DATABASE_TEST_URL)

test_Session = sessionmaker(
    bind=test_engine,
    autoflush=False,
)


def override_get_db():
    db = test_Session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def create_test_table():
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)


@pytest.fixture
def client(create_test_table):
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def sample_application(client):
    response = client.post(
        "/applications",
        json={
            "company_name": "Example Company",
            "job_title": "Backend Developer",
            "applied_date": "2026-10-28",
            "status": "applied",
            "source": "linkedin",
            "job_url": "https://example.com/jobs/123",
            "notes": "Test application",
            "location": "Manila",
            }
        )

    assert response.status_code == 201

    return response.json()