# test_auth.py
from app.security import decode_access_token
from datetime import datetime, timezone, timedelta
import jwt
from app.config import ALGORITHM, SECRET_KEY
from app.security import create_access_token

def test_register_succeed(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "monay.abastas@gmail.com",
            "password": "akoakomonay123"
        }
    )

    assert response.status_code == 201
    assert set(response.json().keys()) == {"id", "email", "created_at"}


def test_duplicate_email(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "monay.abastas@gmail.com",
            "password": "akoakomonay123"
        }
    )

    assert response.status_code == 201

    duplication = client.post(
        "/auth/register",
        json={
            "email": "Monay.abastas@gmail.com",
            "password": "heyheyhey1"
        }
    )

    assert duplication.status_code == 409


def test_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "johnjohn@example.com",
            "password": "1234567"
        }
    )

    assert response.status_code == 422


def test_invalid_email(client):
    response = client.post(
            "/auth/register",
            json={
                "email": "johnexample.com",
                "password": "1234567asda"
            }
        )
    
    assert response.status_code == 422


def test_login_succeed(client, registered_user):
    response = client.post(
        "/auth/login",
        data={"username": registered_user["email"], "password": registered_user["password"]}
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    token = response.json()["access_token"]
    assert decode_access_token(token) == registered_user["id"]


def test_failed_login(client, registered_user):
    detail = "Incorrect email or password"

    wrong_pass = client.post(
            "/auth/login",
            data={"username": registered_user["email"], "password": "not-the-password"}
        )
    
    assert wrong_pass.status_code == 401
    assert wrong_pass.json()["detail"] == detail

    wrong_email = client.post(
        "/auth/login",
        data={"username": "nobody@example.com", "password": registered_user["password"]}
    )

    assert wrong_email.status_code == 401
    assert wrong_email.json()["detail"] == detail


def test_casing_check(client, registered_user):
    response = client.post(
        "/auth/login",
        data={"username": registered_user["email"].swapcase(), "password": registered_user["password"]}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_auth_headers_shape(auth_headers):
    assert auth_headers["Authorization"].startswith("Bearer ")


def test_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_with_garbage_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-token"},
    )

    assert response.status_code == 401


def test_me_with_valid_token(client, registered_user, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == registered_user["email"]
    assert set(data.keys()) == {"id", "email", "created_at"}


def test_me_with_expired_token(client, registered_user):
    expired_payload = {
        "sub": "1",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10)
    }

    token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_me_with_token_for_missing_user(client):
    token = create_access_token(111)

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401