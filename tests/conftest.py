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


def make_auth_headers(client, email: str, password: str) -> dict:
    """Register a user, log in, and return the Authorization header."""
    register = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert login.status_code == 200

    return {"Authorization": f"Bearer {login.json()['access_token']}"}


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
def registered_user(client):
    email = "monaypogi@example.com"
    pword = "aaaaaaaaa"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": pword}
    )

    assert response.status_code == 201

    return {"email": email, "password": pword, "id": response.json()["id"]}


@pytest.fixture
def auth_headers(client, registered_user):
    login = client.post(
        "/auth/login",
        data={"username": registered_user["email"], "password": registered_user["password"]}
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_b(client):
    """A second, separate user (user B)."""
    return make_auth_headers(client, "user-b@example.com", "bbbbbbbbb")


@pytest.fixture
def sample_application(client, auth_headers):
    """An application owned by user A."""
    response = client.post(
        "/applications",
        headers=auth_headers,
        json={
            "company_name": "Example Company",
            "job_title": "Backend Developer",
            "applied_date": "2026-10-28",
            "status": "applied",
            "source": "linkedin",
            "job_url": "https://example.com/jobs/123",
            "notes": "Test application",
            "location": "Manila",
        },
    )

    assert response.status_code == 201

    return response.json()