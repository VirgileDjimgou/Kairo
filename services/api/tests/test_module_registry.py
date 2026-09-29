"""Module Registry coverage: validation, discovery, hooks and role bundles."""

from __future__ import annotations

import uuid

import pytest
from fakes import fake_module_health_check
from helpers import create_tenant_with_user, create_user_for_tenant, login
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.capabilities import capabilities_for_roles
from app.modules.module_registry.descriptor import (
    ModuleDescriptor,
    ModuleRegistry,
    ModuleRegistryError,
    NavigationEntry,
    default_registry,
    validate_capabilities,
)


def _descriptor(key: str, **overrides) -> ModuleDescriptor:
    base = {
        "key": key,
        "name": key.title(),
    }
    base.update(overrides)
    return ModuleDescriptor(**base)  # type: ignore[arg-type]


def test_default_registry_discovers_expected_modules() -> None:
    registry = default_registry()
    keys = set(registry.keys)
    for expected in (
        "membership",
        "contributions",
        "policies",
        "disciplinary",
        "events",
        "announcements",
        "chat",
        "notifications",
        "identity",
        "tenancy",
        "admin",
        "audit",
        "backup",
        "documents",
        "search",
        "sample",
        "module_registry",
    ):
        assert expected in keys

    assert registry.tenant_toggle_keys() == (
        "membership",
        "contributions",
        "policies",
        "disciplinary",
        "events",
        "announcements",
        "chat",
        "notifications",
    )
    assert validate_capabilities(registry) == []


def test_registry_rejects_duplicate_keys() -> None:
    with pytest.raises(ModuleRegistryError, match="Duplicate module key"):
        ModuleRegistry([_descriptor("alpha"), _descriptor("alpha")])


def test_registry_rejects_unknown_dependency() -> None:
    with pytest.raises(ModuleRegistryError, match="unknown module"):
        ModuleRegistry([_descriptor("alpha", depends_on=("missing",))])


def test_registry_rejects_dependency_cycles() -> None:
    with pytest.raises(ModuleRegistryError, match="cycle"):
        ModuleRegistry(
            [
                _descriptor("alpha", depends_on=("beta",)),
                _descriptor("beta", depends_on=("alpha",)),
            ]
        )


def test_registry_rejects_capability_typos() -> None:
    registry = ModuleRegistry([_descriptor("alpha", capabilities=("not:a:capability",))])
    assert validate_capabilities(registry) == ["not:a:capability"]


def test_registry_rejects_duplicate_navigation_keys() -> None:
    entry = NavigationEntry(key="same", label_key="nav.home", path="/dashboard")
    with pytest.raises(ModuleRegistryError, match="Duplicate navigation key"):
        ModuleRegistry(
            [
                _descriptor("alpha", navigation=(entry,)),
                _descriptor("beta", navigation=(entry,)),
            ]
        )


def test_registered_routers_include_multi_router_modules() -> None:
    from app.modules.events.sports_router import router as sports_router
    from app.modules.notifications.router import callback_router

    routers = [router for router, _attr in default_registry().routers()]
    assert sports_router in routers
    assert callback_router in routers
    assert len(routers) >= 17


def test_search_providers_are_composed_in_stable_order() -> None:
    provider_names = [type(provider).__name__ for provider in default_registry().search_providers()]
    assert provider_names == [
        "MembersSearchProvider",
        "DocumentsSearchProvider",
        "EventsSearchProvider",
        "AnnouncementsSearchProvider",
        "PaymentsSearchProvider",
        "ReceiptsSearchProvider",
        "AuditSearchProvider",
        "DisciplineSearchProvider",
    ]


def test_optional_search_and_ai_hooks_are_collected() -> None:
    registry = ModuleRegistry(
        [
            _descriptor(
                "extension",
                search_order=5,
                search_providers=(("fakes", "FakeRegisteredSearchProvider"),),
                ai_context_providers=(("fakes", "FakeRegisteredAiContextProvider"),),
                health_check_module="fakes",
                health_check_attr="fake_module_health_check",
            )
        ]
    )
    providers = registry.search_providers()
    assert [type(provider).__name__ for provider in providers] == [
        "FakeRegisteredSearchProvider"
    ]
    ai_providers = registry.ai_context_providers(db=None)
    assert [type(provider).__name__ for provider in ai_providers] == [
        "FakeRegisteredAiContextProvider"
    ]
    checks = registry.health_checks()
    assert list(checks) == ["extension"]
    assert checks["extension"] is fake_module_health_check


@pytest.mark.asyncio
async def test_modules_endpoint_serves_registry_navigation(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    admin = await create_tenant_with_user(db_session, f"registry-{uuid.uuid4().hex[:6]}")
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"registry-member-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass123!",
        display_name="Registry Member",
        role_code="member",
        profile_type="member",
    )
    await db_session.commit()
    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    member_token = await login(
        client, member["user"].email, member["password"], admin["tenant"].slug
    )

    response = await client.get(
        "/api/v1/modules", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200, response.text
    modules = {module["key"]: module for module in response.json()["modules"]}
    announcements = modules["announcements"]
    assert announcements["enabled"] is True
    assert any(
        entry["key"] == "announcements" and entry["path"] == "/announcements"
        for entry in announcements["navigation"]
    )
    members_entry = next(
        entry for entry in modules["membership"]["navigation"] if entry["key"] == "members"
    )
    assert members_entry["capabilities"] == ["membership:tenant_read"]

    member_response = await client.get(
        "/api/v1/modules", headers={"Authorization": f"Bearer {member_token}"}
    )
    assert member_response.status_code == 200
    member_modules = {
        module["key"]: module for module in member_response.json()["modules"]
    }
    assert member_modules["membership"]["navigation"] == []
    assert any(
        entry["key"] == "notifications"
        for entry in member_modules["notifications"]["navigation"]
    )

    sample = await client.get(
        "/api/v1/modules/sample", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert sample.status_code == 200, sample.text
    assert sample.json()["depends_on"] == ["audit"]


@pytest.mark.asyncio
async def test_sample_module_is_discovered_and_authorized(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    admin = await create_tenant_with_user(db_session, f"sample-{uuid.uuid4().hex[:6]}")
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"sample-member-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass123!",
        display_name="Sample Member",
        role_code="member",
        profile_type="member",
    )
    await db_session.commit()
    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)
    member_token = await login(
        client, member["user"].email, member["password"], admin["tenant"].slug
    )

    allowed = await client.get(
        "/api/v1/sample/status", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert allowed.status_code == 200, allowed.text
    assert allowed.json() == {"module": "sample", "status": "ok"}

    denied = await client.get(
        "/api/v1/sample/status", headers={"Authorization": f"Bearer {member_token}"}
    )
    assert denied.status_code == 403


@pytest.mark.asyncio
async def test_tenant_role_bundle_creation_and_effective_capabilities(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    admin = await create_tenant_with_user(db_session, f"bundle-{uuid.uuid4().hex[:6]}")
    member = await create_user_for_tenant(
        db_session,
        tenant_id=admin["tenant"].id,
        email=f"bundle-member-{uuid.uuid4().hex[:6]}@test.org",
        password="MemberPass123!",
        display_name="Bundle Member",
        role_code="member",
        profile_type="member",
    )
    await db_session.commit()
    admin_token = await login(client, admin["user"].email, admin["password"], admin["tenant"].slug)

    created = await client.post(
        f"/api/v1/tenants/{admin['tenant'].id}/roles",
        json={
            "code": "membership_reader",
            "name": "Membership reader",
            "description": "Read-only directory access for a committee.",
            "capabilities": ["membership:tenant_read", "audit:read"],
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert created.status_code == 201, created.text
    assert set(created.json()["capabilities"]) == {"membership:tenant_read", "audit:read"}
    assert created.json()["is_canonical"] is False

    unknown = await client.post(
        f"/api/v1/tenants/{admin['tenant'].id}/roles",
        json={"code": "bogus_reader", "name": "Bogus", "capabilities": ["bogus:capability"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert unknown.status_code == 422
    assert "bogus:capability" in unknown.json()["detail"]

    reserved = await client.post(
        f"/api/v1/tenants/{admin['tenant'].id}/roles",
        json={"code": "treasurer", "name": "Shadow treasurer", "capabilities": ["audit:read"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert reserved.status_code == 409

    assigned = await client.put(
        f"/api/v1/auth/admin/managed-users/{member['user'].id}/roles",
        json={"role_codes": ["membership_reader"]},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert assigned.status_code == 200, assigned.text

    member_token = await login(
        client, member["user"].email, member["password"], admin["tenant"].slug
    )
    me = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {member_token}"}
    )
    assert me.status_code == 200, me.text
    assert "membership:tenant_read" in me.json()["capabilities"]
    assert "audit:read" in me.json()["capabilities"]

    catalog = await client.get(
        f"/api/v1/tenants/{admin['tenant'].id}/roles",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert catalog.status_code == 200
    bundle = next(role for role in catalog.json() if role["code"] == "membership_reader")
    assert set(bundle["capabilities"]) == {"membership:tenant_read", "audit:read"}


def test_canonical_role_capabilities_remain_available() -> None:
    treasurer = set(capabilities_for_roles(["treasurer"]))
    assert "finance:write" in treasurer
    assert "contribution_receipt:process" in treasurer
    member = set(capabilities_for_roles(["member"]))
    assert "membership:tenant_read" not in member
