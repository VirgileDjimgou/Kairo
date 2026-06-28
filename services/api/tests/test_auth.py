"""
Sprint 1 acceptance tests: auth login and protected endpoint.

Covers:
- Successful login returns JWT with correct claims
- Wrong password returns 401
- Missing token returns 401
- Valid token reaches protected endpoint
- /auth/me returns current user profile
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": data["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0
    assert str(data["tenant"].id) == body["tenant_id"]
    assert str(data["user"].id) == body["user_id"]


@pytest.mark.asyncio
async def test_login_with_tenant_slug(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": data["user"].email,
            "password": data["password"],
            "tenant_slug": data["tenant"].slug,
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": "wrong-password"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@nowhere.com", "password": "irrelevant"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/protected")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    # Log in first
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": data["password"]},
    )
    token = login.json()["access_token"]

    # Call protected endpoint
    response = await client.get(
        "/api/v1/auth/protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Protected endpoint works"
    assert body["tenant_id"] == str(data["tenant"].id)
    assert "admin" in body["roles"]


@pytest.mark.asyncio
async def test_get_me(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": data["user"].email, "password": data["password"]},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == data["user"].email
    assert body["tenant_id"] == str(data["tenant"].id)
    assert "admin" in body["roles"]


@pytest.mark.asyncio
async def test_login_wrong_tenant_slug(
    client: AsyncClient, seeded_tenant_and_admin: dict
) -> None:
    data = seeded_tenant_and_admin
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": data["user"].email,
            "password": data["password"],
            "tenant_slug": "nonexistent-tenant",
        },
    )
    assert response.status_code == 404
