# test_applications.py
from sqlalchemy import null


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


def test_two_records(client):
    record1 = client.post(
        "/applications",
        json={"company_name": 'lipa tech', "job_title": "developer"}
        )

    assert record1.status_code == 201

    record2 = client.post(
        "/applications",
        json={"company_name": 'sanpablo tech', "job_title": "developer maxx"}
        )

    assert record2.status_code == 201

    response = client.get("/applications")

    data = response.json()

    assert len(data) == 2
    assert data[0]["id"] != data[1]["id"]
    assert data[0]["company_name"] == "lipa tech"
    assert data[1]["company_name"] == "sanpablo tech"


def test_optional_fields(client):
    company = "lipa tech"
    job_title = "developer"
    job_url = "https://example.com"
    source = "linkedin"
    notes = "job application test 1"
    loc = "cavite"

    response = client.post(
        "/applications",
        json={"company_name": company, "job_title": job_title, "job_url": job_url, "source": source, "notes": notes, "location": loc}
        )

    assert response.status_code == 201

    record = client.get("/applications/1")

    data = record.json()

    assert data["company_name"] == company
    assert data["job_title"] == job_title
    assert data["job_url"] == "https://example.com/" # HttpUrl normalizes URLs with trailing slash
    assert data["source"] == source
    assert data["location"] == loc
    assert data["notes"] == notes

def test_defaults(client):
    response = client.post(
        "/applications",
        json={"company_name": "comp_name_test", "job_title": "job_title_test"}
        )

    assert response.status_code == 201

    record = client.get(
        "/applications"
    )

    data = record.json()

    assert data[0]["status"] == "applied"
    assert data[0]["source"] is None
    assert data[0]["job_url"] is None
    assert data[0]["notes"] is None
    assert data[0]["location"] is None


def test_patch_changes_only_sent_fields(client, sample_application):
    application_id = sample_application["id"]

    response = client.patch(
        f"/applications/{application_id}",
        json={"status": "offer"},
        )

    assert response.status_code == 200

    updated = response.json()
    expected = {**sample_application, "status": "offer"}

    assert updated == expected

def test_patch_null_required_field(client, sample_application):
    application_id = sample_application["id"]

    response = client.patch(
        f"/applications/{application_id}",
        json={"company_name": None},
    )

    assert response.status_code == 422

def test_patch_missing_id(client):

    response = client.patch(
        "/applications/999",
        json={"status": "rejected"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found!"


def test_patch_empty_body(client, sample_application):
    application_id = sample_application["id"]

    response = client.patch(
        f"/applications/{application_id}",
        json={}
    )

    assert response.status_code == 200
    assert response.json() == sample_application


def test_patch_nullable_field(client, sample_application):
    application_id = sample_application["id"]

    response = client.patch(
        f"/applications/{application_id}",
        json={"notes": None}
    )

    assert response.status_code == 200

    updated = response.json()
    expected = {**sample_application, "notes": None}

    assert updated["notes"] == None
    assert updated == expected

def test_delete(client, sample_application):
    application_id = sample_application["id"]

    deleted = client.delete(
        f"/applications/{application_id}"
    )

    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/applications/{application_id}").status_code == 404

def test_delete_missing_id(client):
    deleted = client.delete("/applications/909")

    assert deleted.status_code == 404

def test_delete_one_of_two_records(client, sample_application):
    first_id = sample_application["id"]

    created = client.post("/applications", json={"company_name": "Another Company", "job_title": "Developer"})
    assert created.status_code == 201
    second_id = created.json()["id"]

    deleted = client.delete(f"/applications/{first_id}")
    assert deleted.status_code == 204

    assert client.get(f"/applications/{second_id}").status_code == 200

    listed = client.get("/applications")
    assert listed.status_code == 200
    assert [record["id"] for record in listed.json()] == [second_id]