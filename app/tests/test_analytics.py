from app.tests.test_links import get_auth_token


def test_analytics_requires_auth(client):
    response = client.get("/links/somecode/analytics")
    assert response.status_code == 401


def test_analytics_tracks_clicks(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    create_response = client.post(
        "/links", json={"original_url": "https://example.com"}, headers=headers
    )
    short_code = create_response.json()["short_code"]

    client.get(f"/{short_code}", follow_redirects=False)
    client.get(f"/{short_code}", follow_redirects=False)
    client.get(f"/{short_code}", follow_redirects=False)

    response = client.get(f"/links/{short_code}/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_clicks"] == 3


def test_analytics_not_found_for_other_users_link(client):
    token_a = get_auth_token(client, "ownera@example.com")
    token_b = get_auth_token(client, "ownerb@example.com")

    create_response = client.post(
        "/links",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    short_code = create_response.json()["short_code"]

    response = client.get(
        f"/links/{short_code}/analytics", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert response.status_code == 404
