"""Auth tests: register, duplicate email, login success/failure, protected routes."""


def test_register_creates_user(client):
    resp = client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "secret123", "full_name": "A"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "a@example.com"
    assert "hashed_password" not in body
    assert "password" not in body


def test_register_duplicate_email_rejected(client):
    payload = {"email": "dup@example.com", "password": "secret123"}
    assert client.post("/auth/register", json=payload).status_code == 201
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_register_short_password_rejected(client):
    resp = client.post(
        "/auth/register", json={"email": "b@example.com", "password": "short"}
    )
    assert resp.status_code == 422


def test_login_returns_token(client):
    client.post("/auth/register", json={"email": "c@example.com", "password": "secret123"})
    resp = client.post(
        "/auth/login", data={"username": "c@example.com", "password": "secret123"}
    )
    assert resp.status_code == 200
    assert resp.json()["token_type"] == "bearer"
    assert resp.json()["access_token"]


def test_login_wrong_password_rejected(client):
    client.post("/auth/register", json={"email": "d@example.com", "password": "secret123"})
    resp = client.post(
        "/auth/login", data={"username": "d@example.com", "password": "wrongpass"}
    )
    assert resp.status_code == 401


def test_protected_route_requires_auth(client):
    resp = client.get("/projects")
    assert resp.status_code == 401


def test_protected_route_rejects_bad_token(client):
    resp = client.get("/projects", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401
