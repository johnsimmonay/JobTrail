# conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import ApplicationStore, get_store

@pytest.fixture
def client():
    store = ApplicationStore()
    app.dependency_overrides[get_store] = lambda: store

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()