"""
Integration tests for the proxy chat endpoint: confirms malicious
prompts are blocked (403) and safe prompts succeed (200), through the
REAL API endpoint — not just calling the pipeline function directly
like we did in test_pipeline.py.
"""


def _get_auth_headers(client, email: str) -> dict:
    """Helper: registers a fresh user and returns ready-to-use auth headers."""
    client.post(
        "/auth/register",
        json={"org_name": "Proxy Test Org", "email": email, "password": "TestPass123!"},
    )
    login_response = client.post(
        "/auth/login", data={"username": email, "password": "TestPass123!"}
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_proxy_blocks_malicious_prompt(client):
    headers = _get_auth_headers(client, "proxytest1@example.com")
    response = client.post(
        "/api/v1/proxy/chat",
        json={"message": "My AWS key is AKIAABCDEFGHIJKLMNOP"},
        headers=headers,
    )
    assert response.status_code == 403


def test_proxy_allows_safe_prompt(client):
    headers = _get_auth_headers(client, "proxytest2@example.com")
    response = client.post(
        "/api/v1/proxy/chat",
        json={"message": "What is the capital of France?"},
        headers=headers,
    )
    assert response.status_code == 200
    assert "response" in response.json()


def test_proxy_rejects_unauthenticated_request(client):
    response = client.post("/api/v1/proxy/chat", json={"message": "Hello"})
    assert response.status_code == 401