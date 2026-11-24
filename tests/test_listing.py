# test_listing.py
# Tests for GET /applications: filtering, search, pagination, ordering, and isolation.
import pytest


def create_app(client, headers, company="Acme", title="Developer", **extra):
    """Create an application and return the response body."""
    response = client.post(
        "/applications",
        headers=headers,
        json={"company_name": company, "job_title": title, **extra},
    )
    assert response.status_code == 201
    return response.json()


def list_apps(client, headers, **params):
    """GET /applications with optional query parameters, returning the JSON body."""
    response = client.get("/applications", headers=headers, params=params)
    assert response.status_code == 200
    return response.json()


# ---------- response shape ----------


def test_list_empty_uses_defaults(client, auth_headers):
    data = list_apps(client, auth_headers)

    assert data == {"items": [], "total": 0, "limit": 20, "offset": 0}


# ---------- status filter ----------


def test_filter_by_status(client, auth_headers):
    create_app(client, auth_headers, "A", status="interview")
    create_app(client, auth_headers, "B", status="interview")
    create_app(client, auth_headers, "C", status="applied")
    create_app(client, auth_headers, "D", status="rejected")

    data = list_apps(client, auth_headers, status="interview")

    assert {item["company_name"] for item in data["items"]} == {"A", "B"}
    assert all(item["status"] == "interview" for item in data["items"])
    assert data["total"] == 2


def test_filter_by_invalid_status(client, auth_headers):
    response = client.get(
        "/applications", headers=auth_headers, params={"status": "banana"}
    )

    assert response.status_code == 422


# ---------- search ----------


def test_search_matches_company_or_title_ignoring_case(client, auth_headers):
    create_app(client, auth_headers, "Shopee", "Backend Engineer")
    create_app(client, auth_headers, "Grab", "Senior SHOPEE Analyst")
    create_app(client, auth_headers, "Lazada", "Developer")

    data = list_apps(client, auth_headers, q="shopee")

    assert {item["company_name"] for item in data["items"]} == {"Shopee", "Grab"}
    assert data["total"] == 2


def test_search_with_no_match(client, auth_headers):
    create_app(client, auth_headers, "Shopee")

    data = list_apps(client, auth_headers, q="zzz-no-such-company")

    assert data["items"] == []
    assert data["total"] == 0


def test_search_percent_is_treated_as_plain_text(client, auth_headers):
    create_app(client, auth_headers, "Acme 100% Corp")
    create_app(client, auth_headers, "Other Corp")

    data = list_apps(client, auth_headers, q="100%")

    assert [item["company_name"] for item in data["items"]] == ["Acme 100% Corp"]
    assert data["total"] == 1


def test_search_underscore_is_treated_as_plain_text(client, auth_headers):
    create_app(client, auth_headers, "Data_Co")
    create_app(client, auth_headers, "DataXCo")

    data = list_apps(client, auth_headers, q="Data_Co")

    assert [item["company_name"] for item in data["items"]] == ["Data_Co"]
    assert data["total"] == 1


def test_filter_and_search_combine(client, auth_headers):
    create_app(client, auth_headers, "Shopee", status="interview")
    create_app(client, auth_headers, "Shopee", status="applied")
    create_app(client, auth_headers, "Grab", status="interview")

    data = list_apps(client, auth_headers, status="interview", q="shopee")

    assert len(data["items"]) == 1
    assert data["items"][0]["company_name"] == "Shopee"
    assert data["items"][0]["status"] == "interview"
    assert data["total"] == 1


# ---------- pagination ----------


def test_pagination_slices_and_total_ignores_limit_and_offset(client, auth_headers):
    # distinct dates make the order explicit: C5 is newest, C1 is oldest
    for i in range(1, 6):
        create_app(client, auth_headers, f"C{i}", applied_date=f"2026-01-0{i}")

    def names(**params):
        data = list_apps(client, auth_headers, **params)
        return [item["company_name"] for item in data["items"]], data

    page1, data1 = names(limit=2, offset=0)
    page2, data2 = names(limit=2, offset=2)
    page3, data3 = names(limit=2, offset=4)
    beyond, data4 = names(limit=2, offset=10)

    assert page1 == ["C5", "C4"]
    assert page2 == ["C3", "C2"]
    assert page3 == ["C1"]
    assert beyond == []

    for data in (data1, data2, data3, data4):
        assert data["total"] == 5

    assert (data2["limit"], data2["offset"]) == (2, 2)


def test_total_counts_filtered_results_not_just_the_page(client, auth_headers):
    for i in range(3):
        create_app(client, auth_headers, f"I{i}", status="interview")
    create_app(client, auth_headers, "Other", status="applied")

    data = list_apps(client, auth_headers, status="interview", limit=1)

    assert len(data["items"]) == 1
    assert data["total"] == 3


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"limit": -1},
        {"limit": "abc"},
        {"offset": -1},
    ],
)
def test_invalid_pagination_params_return_422(client, auth_headers, params):
    response = client.get("/applications", headers=auth_headers, params=params)

    assert response.status_code == 422


# ---------- ordering ----------


def test_default_order_is_newest_applied_date_first(client, auth_headers):
    create_app(client, auth_headers, "Middle", applied_date="2026-02-01")
    create_app(client, auth_headers, "Newest", applied_date="2026-03-01")
    create_app(client, auth_headers, "Oldest", applied_date="2026-01-01")

    data = list_apps(client, auth_headers)

    assert [item["company_name"] for item in data["items"]] == [
        "Newest",
        "Middle",
        "Oldest",
    ]


def test_same_date_falls_back_to_newest_id_first(client, auth_headers):
    ids = [
        create_app(client, auth_headers, f"S{i}", applied_date="2026-05-05")["id"]
        for i in range(3)
    ]

    data = list_apps(client, auth_headers)

    assert [item["id"] for item in data["items"]] == sorted(ids, reverse=True)


# ---------- isolation between users ----------


def test_other_users_records_never_appear_in_items_or_total(
    client, auth_headers, auth_headers_b
):
    a_ids = {
        create_app(client, auth_headers, f"A{i}", status="interview")["id"]
        for i in range(2)
    }
    b_ids = {
        create_app(client, auth_headers_b, f"B{i}", status="interview")["id"]
        for i in range(3)
    }

    data_a = list_apps(client, auth_headers)
    data_b = list_apps(client, auth_headers_b)

    assert {item["id"] for item in data_a["items"]} == a_ids
    assert data_a["total"] == 2
    assert {item["id"] for item in data_b["items"]} == b_ids
    assert data_b["total"] == 3

    # the same holds when filtering and searching
    filtered = list_apps(client, auth_headers, status="interview")
    assert filtered["total"] == 2

    searched = list_apps(client, auth_headers, q="B0")
    assert searched["items"] == []
    assert searched["total"] == 0