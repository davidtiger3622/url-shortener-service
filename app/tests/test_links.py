def get_auth_token(client, email="linkuser@example.com", password="password123"):
    client.post("/auth/register", json={"email": email, "password": password})
    response = client.post("/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]


def test_create_link_requires_auth(client):
    response = client.post("/links", json={"original_url": "https://example.com"})
    assert response.status_code == 401


def test_create_link_success(client):
    token = get_auth_token(client)
    response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://example.com"
    assert len(data["short_code"]) == 6
    assert data["is_active"] is True


def test_list_links_pagination(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    for i in range(3):
        client.post("/links", json={"original_url": f"https://example.com/{i}"}, headers=headers)

    response = client.get("/links?page=1&page_size=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["page_size"] == 2
    assert len(data["items"]) == 2


def test_list_links_only_shows_own_links(client):
    token_a = get_auth_token(client, "usera@example.com")
    token_b = get_auth_token(client, "userb@example.com")

    client.post(
        "/links",
        json={"original_url": "https://a.com"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    response = client.get("/links", headers={"Authorization": f"Bearer {token_b}"})
    assert response.json()["total"] == 0


def test_redirect_to_original_url(client):
    token = get_auth_token(client)
    create_response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    short_code = create_response.json()["short_code"]

    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com"


def test_redirect_nonexistent_code(client):
    response = client.get("/doesnotexist", follow_redirects=False)
    assert response.status_code == 404


def test_redirect_expired_link(client):
    token = get_auth_token(client)
    create_response = client.post(
        "/links",
        json={"original_url": "https://example.com", "expires_at": "2020-01-01T00:00:00Z"},
        headers={"Authorization": f"Bearer {token}"},
    )
    short_code = create_response.json()["short_code"]

    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 410
