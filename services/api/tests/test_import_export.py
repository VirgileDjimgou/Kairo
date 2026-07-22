import csv
import io
import uuid as _uuid
from datetime import UTC

import pytest
from httpx import AsyncClient

from app.core.import_export import ImportResult, generate_csv, parse_csv

pytestmark = pytest.mark.asyncio


async def _login(client: AsyncClient, email: str, password: str, tenant_id: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_id": tenant_id},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


async def _create_tenant(db_session):
    from app.modules.tenancy.models import Tenant
    tenant = Tenant(
        id=_uuid.uuid4(),
        slug=f"ie-test-{_uuid.uuid4().hex[:8]}",
        name="Import Export Test",
        type="association",
    )
    db_session.add(tenant)
    await db_session.flush()
    return tenant


async def _create_admin(db_session, tenant):
    from app.core.security import hash_password
    from app.modules.identity.models import User
    from app.modules.tenancy.models import Role, TenantUser, user_roles
    user = User(
        id=_uuid.uuid4(),
        email=f"ie-admin-{_uuid.uuid4().hex[:6]}@test.org",
        password_hash=hash_password("TestPass123!"),
        display_name="IE Admin",
        status="active",
    )
    db_session.add(user)
    await db_session.flush()
    role = Role(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        code="admin",
        name="Administrator",
        is_system_role=True,
    )
    db_session.add(role)
    await db_session.flush()
    membership = TenantUser(
        id=_uuid.uuid4(),
        tenant_id=tenant.id,
        user_id=user.id,
        profile_type="admin",
        membership_status="active",
    )
    db_session.add(membership)
    await db_session.flush()
    await db_session.execute(
        user_roles.insert().values(tenant_user_id=membership.id, role_id=role.id)
    )
    await db_session.flush()
    return user, tenant


async def _auth_headers(client, user, tenant):
    token = await _login(client, user.email, "TestPass123!", str(tenant.id))
    return {"Authorization": f"Bearer {token}"}


# ── Core utility tests ────────────────────────────────────────────────────────


class TestCoreImportExport:

    def test_parse_csv_basic(self):
        csv_data = "member_code,first_name,last_name\nM001,John,Doe\nM002,Jane,Smith\n"
        rows = parse_csv(csv_data.encode())
        assert len(rows) == 2
        assert rows[0]["member_code"] == "M001"
        assert rows[1]["last_name"] == "Smith"

    def test_parse_csv_empty(self):
        rows = parse_csv(b"")
        assert rows == []

    def test_parse_csv_bom(self):
        csv_data = "member_code,name\nM001,John\n"
        rows = parse_csv(csv_data.encode("utf-8-sig"))
        assert len(rows) == 1
        assert rows[0]["member_code"] == "M001"

    def test_generate_csv_basic(self):
        rows = [{"name": "John", "age": "30"}, {"name": "Jane", "age": "25"}]
        result = generate_csv(rows)
        assert "name,age" in result
        assert "John,30" in result
        assert "Jane,25" in result

    def test_generate_csv_empty(self):
        assert generate_csv([]) == ""

    def test_generate_csv_with_fieldnames(self):
        rows = [{"name": "John", "extra": "x"}]
        result = generate_csv(rows, fieldnames=["name"])
        assert "name" in result
        assert "extra" not in result


# ── Member import tests ───────────────────────────────────────────────────────


class TestMemberImport:

    async def test_import_dry_run_returns_validation(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)

        csv_content = (
            "member_code,first_name,last_name,email\n"
            "M001,John,Doe,john@test.com\n"
            "M002,Jane,Smith,jane@test.com\n"
        )
        resp = await client.post(
            "/api/v1/memberships/import?dry_run=true",
            headers=headers,
            files={"file": ("members.csv", csv_content, "text/csv")},
        )
        assert resp.status_code == 200, resp.text
        result = ImportResult.model_validate(resp.json())
        assert result.dry_run is True
        assert result.total_rows == 2
        assert result.success_count == 2
        assert result.error_count == 0

    async def test_import_creates_profiles(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)

        csv_content = (
            "member_code,first_name,last_name,email,status\n"
            "M001,John,Doe,john@test.com,active\n"
            "M002,Jane,Smith,jane@test.com,active\n"
        )
        resp = await client.post(
            "/api/v1/memberships/import",
            headers=headers,
            files={"file": ("members.csv", csv_content, "text/csv")},
        )
        assert resp.status_code == 200, resp.text
        result = ImportResult.model_validate(resp.json())
        assert result.dry_run is False
        assert result.total_rows == 2
        assert result.success_count == 2
        assert result.error_count == 0

        resp2 = await client.get("/api/v1/memberships/", headers=headers)
        assert resp2.status_code == 200
        profiles = resp2.json()
        assert len(profiles) == 2

    async def test_import_missing_required_fields(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)

        csv_content = (
            "member_code,first_name,last_name\n"
            "M001,,Doe\n"  # missing first_name
            "M002,Jane,\n"  # missing last_name
        )
        resp = await client.post(
            "/api/v1/memberships/import?dry_run=true",
            headers=headers,
            files={"file": ("members.csv", csv_content, "text/csv")},
        )
        assert resp.status_code == 200, resp.text
        result = ImportResult.model_validate(resp.json())
        assert result.total_rows == 2
        assert result.error_count == 2

    async def test_import_duplicate_member_code(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)

        csv_content = (
            "member_code,first_name,last_name\n"
            "DUP01,John,Doe\n"
        )
        resp = await client.post(
            "/api/v1/memberships/import",
            headers=headers,
            files={"file": ("members.csv", csv_content, "text/csv")},
        )
        assert resp.status_code == 200, resp.text

        resp2 = await client.post(
            "/api/v1/memberships/import",
            headers=headers,
            files={"file": ("members.csv", csv_content, "text/csv")},
        )
        assert resp2.status_code == 200
        result = ImportResult.model_validate(resp2.json())
        assert result.error_count == 1

    async def test_import_tenant_isolation(self, client, db_session):
        tenant_a = await _create_tenant(db_session)
        tenant_b = await _create_tenant(db_session)
        user_a, _ = await _create_admin(db_session, tenant_a)
        user_b, _ = await _create_admin(db_session, tenant_b)
        headers_a = await _auth_headers(client, user_a, tenant_a)
        headers_b = await _auth_headers(client, user_b, tenant_b)

        csv = "member_code,first_name,last_name\nTA01,Alice,Alpha\n"
        resp_a = await client.post(
            "/api/v1/memberships/import",
            headers=headers_a,
            files={"file": ("m.csv", csv, "text/csv")},
        )
        assert resp_a.status_code == 200

        resp_b_list = await client.get("/api/v1/memberships/", headers=headers_b)
        assert len(resp_b_list.json()) == 0


# ── Member export tests ───────────────────────────────────────────────────────


class TestMemberExport:

    async def test_export_returns_csv(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)

        csv_in = "member_code,first_name,last_name,email,status\nEXP01,John,Doe,j@t.com,active\n"
        await client.post(
            "/api/v1/memberships/import",
            headers=headers,
            files={"file": ("m.csv", csv_in, "text/csv")},
        )

        resp = await client.get("/api/v1/memberships/export", headers=headers)
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert "Content-Disposition" in resp.headers

        reader = csv.DictReader(io.StringIO(resp.text))
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["member_code"] == "EXP01"


# ── Contribution import tests ─────────────────────────────────────────────────


class TestContributionImport:

    async def test_import_contributions(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)

        # First import a member
        csv_member = "member_code,first_name,last_name\nCM01,Charles,Ming\n"
        await client.post(
            "/api/v1/memberships/import",
            headers=headers,
            files={"file": ("m.csv", csv_member, "text/csv")},
        )

        csv_contrib = (
            "member_code,year,expected_amount,paid_amount,currency,status\n"
            "CM01,2026,100.00,50.00,EUR,partial\n"
        )
        resp = await client.post(
            "/api/v1/contributions/import",
            headers=headers,
            files={"file": ("contrib.csv", csv_contrib, "text/csv")},
        )
        assert resp.status_code == 200, resp.text
        result = ImportResult.model_validate(resp.json())
        assert result.success_count == 1
        assert result.error_count == 0

    async def test_import_requires_admin_role(self, client, db_session):
        tenant = await _create_tenant(db_session)
        from app.core.security import hash_password
        from app.modules.identity.models import User
        from app.modules.tenancy.models import TenantUser
        user = User(
            id=_uuid.uuid4(),
            email=f"nonadmin-{_uuid.uuid4().hex[:6]}@test.org",
            password_hash=hash_password("TestPass123!"),
            display_name="Non Admin",
            status="active",
        )
        db_session.add(user)
        await db_session.flush()
        membership = TenantUser(
            id=_uuid.uuid4(), tenant_id=tenant.id, user_id=user.id, profile_type="member", membership_status="active",
        )
        db_session.add(membership)
        await db_session.flush()
        token = await _login(client, user.email, "TestPass123!", str(tenant.id))
        headers = {"Authorization": f"Bearer {token}"}
        csv = "member_code,first_name,last_name\nM001,Test,User\n"
        resp = await client.post(
            "/api/v1/memberships/import",
            headers=headers,
            files={"file": ("m.csv", csv, "text/csv")},
        )
        assert resp.status_code == 403

        resp2 = await client.post(
            "/api/v1/contributions/import",
            headers=headers,
            files={"file": ("c.csv", csv, "text/csv")},
        )
        assert resp2.status_code == 403

    async def test_import_contributions_unknown_member(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)

        csv = "member_code,year,expected_amount,paid_amount\nUNKNOWN,2026,100,0\n"
        resp = await client.post(
            "/api/v1/contributions/import?dry_run=true",
            headers=headers,
            files={"file": ("c.csv", csv, "text/csv")},
        )
        assert resp.status_code == 200, resp.text
        result = ImportResult.model_validate(resp.json())
        assert result.error_count == 1


# ── Export tests ──────────────────────────────────────────────────────────────


class TestExports:

    async def _seed_event(self, client, headers, tenant):
        from datetime import datetime
        resp = await client.post(
            "/api/v1/events/",
            headers=headers,
            json={
                "title": "Test Event",
                "start_at": datetime.now(UTC).isoformat(),
                "visibility_scope": "members_only",
                "status": "published",
            },
        )
        return resp

    async def test_export_events_csv(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)
        await self._seed_event(client, headers, tenant)

        resp = await client.get("/api/v1/events/export", headers=headers)
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]

    async def test_export_announcements_csv(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)
        resp = await client.post(
            "/api/v1/announcements/",
            headers=headers,
            json={"title": "Test", "body": "Body text"},
        )
        assert resp.status_code == 201

        resp2 = await client.get("/api/v1/announcements/export", headers=headers)
        assert resp2.status_code == 200
        assert "text/csv" in resp2.headers["content-type"]

    async def test_export_contributions_csv(self, client, db_session):
        tenant = await _create_tenant(db_session)
        user, _ = await _create_admin(db_session, tenant)
        headers = await _auth_headers(client, user, tenant)

        csv_member = "member_code,first_name,last_name\nEC01,Export,Contrib\n"
        await client.post(
            "/api/v1/memberships/import",
            headers=headers,
            files={"file": ("m.csv", csv_member, "text/csv")},
        )
        csv_contrib = "member_code,year,expected_amount,paid_amount\nEC01,2026,200,100\n"
        await client.post(
            "/api/v1/contributions/import",
            headers=headers,
            files={"file": ("c.csv", csv_contrib, "text/csv")},
        )

        resp = await client.get("/api/v1/contributions/export", headers=headers)
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]

    async def test_export_members_forbidden_for_plain_member(self, client, db_session):
        tenant = await _create_tenant(db_session)
        from app.core.security import hash_password
        from app.modules.identity.models import User
        from app.modules.tenancy.models import TenantUser
        user = User(
            id=_uuid.uuid4(),
            email=f"member-{_uuid.uuid4().hex[:6]}@test.org",
            password_hash=hash_password("TestPass123!"),
            display_name="Plain Member",
            status="active",
        )
        db_session.add(user)
        await db_session.flush()
        membership = TenantUser(
            id=_uuid.uuid4(), tenant_id=tenant.id, user_id=user.id, profile_type="member", membership_status="active",
        )
        db_session.add(membership)
        await db_session.flush()
        token = await _login(client, user.email, "TestPass123!", str(tenant.id))
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/api/v1/memberships/export", headers=headers)
        assert resp.status_code == 403
