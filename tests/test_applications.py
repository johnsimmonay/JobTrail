# test_applications.py
def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": 1}
    

def test_create_applications(client):
    response = client.post(
        "/applications",
        json={"company_name": "dxc", "job_title": "junior dev"},
    )

    data = response.json()

    assert response.status_code == 201
    assert "id" in data
    assert "created_at" in data
    assert data["company_name"] == "dxc"

def test_empty_company_name(client):
    response = client.post(
        "/applications",
        json={"company_name": "", "job_title": "dev"},
    )

    assert response.status_code == 422

def test_invalid_status(client):
    response = client.post(
        "/applications",
        json={"company_name": "ddd", "job_title": "dev max", "status": "APPLYING"}
    )

    assert response.status_code == 422

def test_created_id(client):
    create_response = client.post(
        "/applications",
        json={"company_name": "dxc", "job_title": "junior dev"},
    )

    assert create_response.status_code == 201
    created = create_response.json()


    get_response = client.get(
        f"/applications/{created["id"]}"
    )

    assert get_response.status_code == 200
    assert get_response.json() == created


def test_nonexistent_application(client):
    response = client.get("/applications/9999")

    assert response.status_code == 404
