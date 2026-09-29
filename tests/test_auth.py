"""
Integration tests for the auth flow: register creates an org + admin
user, login returns a valid JWT, and protected endpoints correctly
reject requests without a valid token.
"""


def test_register_creates_admin_user(client):
    response = client.post(
        "/auth/register",
        json={
            "org_name": "Test Org",
            "email": "testuser@example.com",
            "password": "TestPass123!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["role"] == "admin"


def test_register_rejects_duplicate_email(client):
    # First registration should succeed.
    client.post(
        "/auth/register",
        json={"org_name": "Org A", "email": "dup@example.com", "password": "TestPass123!"},
    )
    # Second registration with the SAME email should fail.
    response = client.post(
        "/auth/register",
        json={"org_name": "Org B", "email": "dup@example.com", "password": "TestPass123!"},
    )
    assert response.status_code == 400


def test_login_returns_valid_token(client):
    client.post(
        "/auth/register",
        json={"org_name": "Login Org", "email": "logintest@example.com", "password": "TestPass123!"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "logintest@example.com", "password": "TestPass123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_rejects_wrong_password(client):
    client.post(
        "/auth/register",
        json={"org_name": "Wrong Pass Org", "email": "wrongpass@example.com", "password": "TestPass123!"},
    )
    response = client.post(
        "/auth/login",
        data={"username": "wrongpass@example.com", "password": "IncorrectPassword"},
    )
    assert response.status_code == 401


def test_protected_endpoint_rejects_no_token(client):
    response = client.get("/api/v1/me")
    assert response.status_code == 401


def test_protected_endpoint_accepts_valid_token(client):
    client.post(
        "/auth/register",
        json={"org_name": "Me Org", "email": "metest@example.com", "password": "TestPass123!"},
    )
    login_response = client.post(
        "/auth/login",
        data={"username": "metest@example.com", "password": "TestPass123!"},
    )
    token = login_response.json()["access_token"]

    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "metest@example.com"