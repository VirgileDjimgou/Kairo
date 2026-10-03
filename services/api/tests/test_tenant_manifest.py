"""Tenant-aware Web App Manifest: public branding, defaults and isolation."""

from __future__ import annotations

import json

import pytest
from helpers import create_tenant_with_user
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tenancy.models import Tenant

BRANDING = {
    "display_name": "COMBIS App",
    "short_name": "COMBIS",
    "theme_color": "#0a5c2e",
    "background_color": "#f4f7f2",
    "icon_192_url": "/assets/combis-192.png",
    "icon_512_url": "https://cdn.example.org/combis-512.png",
    "maskable_icon_url": "/assets/combis-maskable.png",
}


@pytest.mark.asyncio
async def test_manifest_uses_tenant_branding(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "manifest-branded")
    tenant = await db_session.get(Tenant, context["tenant"].id)
    assert tenant is not None
    tenant.branding_json = json.dumps(BRANDING)  # type: ignore[assignment]
    await db_session.commit()

    response = await client.get(f"/api/v1/tenants/public/{tenant.slug}/manifest")

    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/manifest+json")
    body = response.json()
    assert body["name"] == "COMBIS App"
    assert body["short_name"] == "COMBIS"
    assert body["theme_color"] == "#0a5c2e"
    assert body["background_color"] == "#f4f7f2"
    assert body["display"] == "standalone"
    assert body["start_url"] == "/dashboard"
    assert body["scope"] == "/"
    assert body["lang"] == "fr"

    icons = body["icons"]
    base = str(client.base_url).rstrip("/")
    sources = {icon["src"] for icon in icons}
    assert f"{base}/assets/combis-192.png" in sources
    # Absolute external icons are preserved as-is.
    assert "https://cdn.example.org/combis-512.png" in sources
    maskable = [icon for icon in icons if icon["purpose"] == "maskable"]
    assert maskable and maskable[0]["src"].endswith("/assets/combis-maskable.png")


@pytest.mark.asyncio
async def test_manifest_defaults_to_safe_kairo_values(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "manifest-default")
    tenant = await db_session.get(Tenant, context["tenant"].id)
    assert tenant is not None

    response = await client.get(f"/api/v1/tenants/public/{tenant.slug}/manifest")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["name"] == "Kairo"
    assert body["short_name"] == "Kairo"
    assert body["theme_color"] == "#1a3f6b"
    icon_sources = {icon["src"] for icon in body["icons"]}
    base = str(client.base_url).rstrip("/")
    assert icon_sources == {
        f"{base}/pwa-192x192.png",
        f"{base}/pwa-512x512.png",
    }
    purposes = {icon["purpose"] for icon in body["icons"]}
    assert purposes == {"any", "maskable"}


@pytest.mark.asyncio
async def test_manifest_requires_an_active_tenant(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    missing = await client.get("/api/v1/tenants/public/no-such-tenant/manifest")
    assert missing.status_code == 404

    context = await create_tenant_with_user(db_session, "manifest-inactive")
    tenant = await db_session.get(Tenant, context["tenant"].id)
    assert tenant is not None
    tenant.status = "suspended"
    await db_session.commit()

    inactive = await client.get(f"/api/v1/tenants/public/{tenant.slug}/manifest")
    assert inactive.status_code == 404


@pytest.mark.asyncio
async def test_manifest_is_public_and_exposes_branding_only(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    context = await create_tenant_with_user(db_session, "manifest-public")
    tenant = await db_session.get(Tenant, context["tenant"].id)
    assert tenant is not None
    tenant.branding_json = json.dumps(BRANDING)  # type: ignore[assignment]
    await db_session.commit()

    # No Authorization header: the manifest must be installable before sign-in.
    response = await client.get(f"/api/v1/tenants/public/{tenant.slug}/manifest")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "name",
        "short_name",
        "description",
        "lang",
        "theme_color",
        "background_color",
        "display",
        "orientation",
        "start_url",
        "scope",
        "icons",
    }
    raw = response.text.lower()
    assert "role" not in raw
    assert "module" not in raw
    assert "member" not in raw
    assert "settings" not in raw
