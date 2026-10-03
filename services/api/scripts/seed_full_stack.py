"""Seed the deterministic full-stack release-gate tenants (Roadmap V2 S128).

Creates the COMBIS pilot tenant (roles, branding, custom domain) and a Tenant X
isolation control, then prints a JSON summary. Idempotent: existing gate tenants
and gate accounts are removed first so the scenario always starts from the same
state. This script is only used by the release-gate environment.

Usage (inside the API container):
    python /app/scripts/seed_full_stack.py
"""

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from sqlalchemy import delete, select  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.session import async_session_factory  # noqa: E402
from app.modules.identity.models import User  # noqa: E402
from app.modules.tenancy.models import Tenant  # noqa: E402
from app.modules.tenancy.module_toggles import default_module_toggles  # noqa: E402
from app.modules.tenancy.repository import TenancyRepository  # noqa: E402

COMBIS_SLUG = "combis"
COMBIS_NAME = "Combis Sport Verein"
COMBIS_CUSTOM_DOMAIN = "app.combis.test"
TENANT_X_SLUG = "tenant-x"
TENANT_X_NAME = "Tenant X Isolation Control"

COMBIS_BRANDING = {
    "display_name": "COMBIS App",
    "short_name": "COMBIS",
    "legal_name": "Combis Sport Verein e.V.",
    "notification_name": "COMBIS",
    "primary_color": "#0a5c2e",
    "secondary_color": "#c93146",
    "background_color": "#f4f7f2",
    "theme_color": "#0a5c2e",
    "favicon_url": "/favicon.svg",
    "support_name": "COMBIS Support",
    "support_email": "support@combis.kairo.app",
    "custom_domain": COMBIS_CUSTOM_DOMAIN,
}

ACCOUNTS: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "combis-admin@gate.kairo.app",
        "GateAdmin1!",
        "Gate Admin",
        COMBIS_SLUG,
        "principal_admin",
    ),
    (
        "combis-secretary@gate.kairo.app",
        "GateSecretary1!",
        "Gate Secretary",
        COMBIS_SLUG,
        "secretary_general",
    ),
    (
        "combis-treasurer@gate.kairo.app",
        "GateTreasurer1!",
        "Gate Treasurer",
        COMBIS_SLUG,
        "treasurer",
    ),
    (
        "tenantx-admin@gate.kairo.app",
        "GateTenantX1!",
        "Tenant X Admin",
        TENANT_X_SLUG,
        "member",
    ),
)


async def _reset(session) -> None:
    for slug in (COMBIS_SLUG, TENANT_X_SLUG):
        tenant = await session.scalar(select(Tenant).where(Tenant.slug == slug))
        if tenant is not None:
            await session.execute(delete(Tenant).where(Tenant.id == tenant.id))
    emails = [email for email, _, _, _, _ in ACCOUNTS]
    await session.execute(delete(User).where(User.email.in_(emails)))
    await session.flush()


async def _create_tenant(
    session,
    slug: str,
    name: str,
    branding: dict,
    custom_domain: str | None,
) -> Tenant:
    tenant = Tenant(
        id=uuid.uuid4(),
        slug=slug,
        name=name,
        type="association",
        status="active",
        default_language="fr",
        custom_domain=custom_domain,
        branding_json=json.dumps(branding),
        settings_json=json.dumps({"modules": default_module_toggles()}),
    )
    session.add(tenant)
    await session.flush()
    return tenant


async def _create_account(
    session,
    tenant: Tenant,
    email: str,
    password: str,
    display_name: str,
    role_code: str,
) -> None:
    repo = TenancyRepository(session)
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash=hash_password(password),
        display_name=display_name,
        status="active",
    )
    session.add(user)
    await session.flush()

    roles = {role.code: role for role in await repo.ensure_canonical_role_catalog(tenant.id)}
    role = roles.get(role_code)
    if role is None:
        raise SystemExit(f"Canonical role {role_code} is unavailable for tenant {tenant.slug}")

    await repo.create_tenant_user(
        tenant.id,
        user.id,
        profile_type="admin" if role_code in {"principal_admin", "admin"} else "member",
    )
    await repo.assign_role_to_user(tenant.id, user.id, role.id)


async def seed() -> dict[str, object]:
    async with async_session_factory() as session:
        await _reset(session)
        combis = await _create_tenant(
            session,
            COMBIS_SLUG,
            COMBIS_NAME,
            COMBIS_BRANDING,
            COMBIS_CUSTOM_DOMAIN,
        )
        tenant_x = await _create_tenant(session, TENANT_X_SLUG, TENANT_X_NAME, {}, None)
        for email, password, display_name, tenant_slug, role_code in ACCOUNTS:
            tenant = combis if tenant_slug == COMBIS_SLUG else tenant_x
            await _create_account(session, tenant, email, password, display_name, role_code)
        await session.commit()

    return {
        "combis": {
            "slug": COMBIS_SLUG,
            "tenant_id": str(combis.id),
            "custom_domain": COMBIS_CUSTOM_DOMAIN,
        },
        "tenant_x": {"slug": TENANT_X_SLUG, "tenant_id": str(tenant_x.id)},
        "accounts": [
            {"email": email, "password": password, "tenant": tenant_slug, "role": role_code}
            for email, password, _, tenant_slug, role_code in ACCOUNTS
        ],
    }


def main() -> int:
    summary = asyncio.run(seed())
    print("GATE_SEED " + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
