# test_auth.py
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