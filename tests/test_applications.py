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