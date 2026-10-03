"""Host-based tenant resolution: explicit mapping, no client override, isolation."""

from __future__ import annotations

import pytest
from helpers import create_tenant_with_user, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.tenancy.models import Tenant


async def _assign_custom_domain(
    client: AsyncClient,
    tenant_id,
    email: str,
    password: str,
    domain: str,
) -> None:
    token = await login(client, email, password)
    response = await client.put(
        f"/api/v1/tenants/{tenant_id}/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={"branding": {"custom_domain": domain, "display_name": "COMBIS App"}},
    )
    assert response.status_code == 200, response.text


@pytest.mark.asyncio
async def test_custom_domain_resolves_the_tenant(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "domain-custom")
    await _assign_custom_domain(
        client, context["tenant"].id, context["user"].email, context["password"], "app.customer-domain.de"
    )

    response = await client.get(
        "/api/v1/tenants/public/resolve",
        headers={"Host": "app.customer-domain.de"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["slug"] == context["tenant"].slug
    assert body["name"] == context["tenant"].name
    assert body["branding"]["display_name"] == "COMBIS App"
    assert body["manifest_url"].endswith(f"/tenants/public/{context['tenant'].slug}/manifest")


@pytest.mark.asyncio
async def test_host_normalization_accepts_port_and_case(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "domain-normalize")
    await _assign_custom_domain(
        client, context["tenant"].id, context["user"].email, context["password"], "app.normalize-domain.de"
    )

    response = await client.get(
        "/api/v1/tenants/public/resolve",
        headers={"Host": "APP.Normalize-Domain.DE:8443"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["slug"] == context["tenant"].slug


@pytest.mark.asyncio
async def test_platform_subdomain_resolves_direct_slugs_only(
    client: AsyncClient, db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "platform_base_domain", "kairo.example")
    context = await create_tenant_with_user(db_session, "domain-sub")

    direct = await client.get(
        "/api/v1/tenants/public/resolve",
        headers={"Host": f"{context['tenant'].slug}.kairo.example"},
    )
    assert direct.status_code == 200, direct.text
    assert direct.json()["slug"] == context["tenant"].slug

    nested = await client.get(
        "/api/v1/tenants/public/resolve",
        headers={"Host": f"extra.{context['tenant'].slug}.kairo.example"},
    )
    assert nested.status_code == 404

    unknown = await client.get(
        "/api/v1/tenants/public/resolve",
        headers={"Host": "no-such-tenant.kairo.example"},
    )
    assert unknown.status_code == 404


@pytest.mark.asyncio
async def test_unknown_host_cannot_select_a_tenant(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await client.get(
        "/api/v1/tenants/public/resolve",
        headers={"Host": "unknown.example.org"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_client_override_is_ignored(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    tenant_a = await create_tenant_with_user(db_session, "domain-a")
    tenant_b = await create_tenant_with_user(db_session, "domain-b")
    await _assign_custom_domain(
        client, tenant_a["tenant"].id, tenant_a["user"].email, tenant_a["password"], "tenant-a.example.org"
    )

    response = await client.get(
        f"/api/v1/tenants/public/resolve?tenant={tenant_b['tenant'].slug}&slug={tenant_b['tenant'].slug}",
        headers={"Host": "tenant-a.example.org"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["slug"] == tenant_a["tenant"].slug


@pytest.mark.asyncio
async def test_custom_domain_is_unique_across_tenants(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    tenant_a = await create_tenant_with_user(db_session, "domain-unique-a")
    tenant_b = await create_tenant_with_user(db_session, "domain-unique-b")
    await _assign_custom_domain(
        client, tenant_a["tenant"].id, tenant_a["user"].email, tenant_a["password"], "shared.example.org"
    )

    token_b = await login(client, tenant_b["user"].email, tenant_b["password"])
    conflict = await client.put(
        f"/api/v1/tenants/{tenant_b['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"branding": {"custom_domain": "shared.example.org"}},
    )
    assert conflict.status_code == 409

    # The same tenant may keep or re-save its own domain.
    token_a = await login(client, tenant_a["user"].email, tenant_a["password"])
    keep = await client.put(
        f"/api/v1/tenants/{tenant_a['tenant'].id}/settings",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"branding": {"custom_domain": "shared.example.org"}},
    )
    assert keep.status_code == 200


@pytest.mark.asyncio
async def test_inactive_tenant_domain_does_not_resolve(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "domain-inactive")
    await _assign_custom_domain(
        client, context["tenant"].id, context["user"].email, context["password"], "inactive.example.org"
    )

    tenant = await db_session.get(Tenant, context["tenant"].id)
    assert tenant is not None
    tenant.status = "suspended"
    await db_session.commit()

    response = await client.get(
        "/api/v1/tenants/public/resolve",
        headers={"Host": "inactive.example.org"},
    )
    assert response.status_code == 404
