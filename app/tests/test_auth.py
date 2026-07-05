def test_register_user(client):
    response = client.post(
        "/auth/register", json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "password123"})
    response = client.post(
        "/auth/register", json={"email": "dup@example.com", "password": "password456"}
    )
    assert response.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "password123"})
    response = client.post(
        "/auth/login", data={"username": "login@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "wrong@example.com", "password": "password123"})
    response = client.post(
        "/auth/login", data={"username": "wrong@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401
