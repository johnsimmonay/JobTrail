# test_ownership.py
# Tests that authentication is required and that users can only touch their own data.


def test_applications_require_token(client):
    assert client.get("/applications").status_code == 401
    assert client.get("/applications/1").status_code == 401
    assert client.post(
        "/applications", json={"company_name": "x", "job_title": "y"}
    ).status_code == 401
    assert client.patch("/applications/1", json={"status": "offer"}).status_code == 401
    assert client.delete("/applications/1").status_code == 401


def test_other_user_cannot_read(client, sample_application, auth_headers_b):
    response = client.get(
        f"/applications/{sample_application['id']}",
        headers=auth_headers_b,
    )

    assert response.status_code == 404


def test_other_user_cannot_patch(client, sample_application, auth_headers_b):
    response = client.patch(
        f"/applications/{sample_application['id']}",
        headers=auth_headers_b,
        json={"status": "rejected"},
    )

    assert response.status_code == 404


def test_other_user_cannot_delete(client, sample_application, auth_headers_b):
    response = client.delete(
        f"/applications/{sample_application['id']}",
        headers=auth_headers_b,
    )

    assert response.status_code == 404


def test_list_only_returns_own_records(
    client, auth_headers, auth_headers_b, sample_application
):
    created_b = client.post(
        "/applications",
        headers=auth_headers_b,
        json={"company_name": "B Company", "job_title": "B Developer"},
    )
    assert created_b.status_code == 201

    list_b = client.get("/applications", headers=auth_headers_b)
    assert list_b.status_code == 200
    assert [r["id"] for r in list_b.json()["items"]] == [created_b.json()["id"]]

    list_a = client.get("/applications", headers=auth_headers)
    assert [r["id"] for r in list_a.json()["items"]] == [sample_application["id"]]


def test_record_unchanged_after_other_user_attempts(
    client, auth_headers, auth_headers_b, sample_application
):
    app_id = sample_application["id"]

    client.patch(
        f"/applications/{app_id}",
        headers=auth_headers_b,
        json={"status": "rejected", "company_name": "Hacked"},
    )
    client.delete(f"/applications/{app_id}", headers=auth_headers_b)

    response = client.get(f"/applications/{app_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == sample_application


def test_user_id_in_body_is_ignored(
    client, auth_headers, auth_headers_b, registered_user
):
    # user A creates a record while claiming it belongs to someone else
    response = client.post(
        "/applications",
        headers=auth_headers,
        json={"company_name": "Mine", "job_title": "Dev", "user_id": 999},
    )

    assert response.status_code == 201
    assert "user_id" not in response.json()

    app_id = response.json()["id"]

    # A can still read it, so it is owned by A
    assert client.get(f"/applications/{app_id}", headers=auth_headers).status_code == 200
    # B cannot, so it was not reassigned
    assert client.get(f"/applications/{app_id}", headers=auth_headers_b).status_code == 404