"""
Database seed script — idempotent demo tenant and admin user.

Run once after migrations:
    docker compose exec api python -m app.db.seed

Creates:
  - Tenant:  slug="demo", name="Demo Organization"
  - User:    admin@demo.org / Admin123!  (display: "Admin User")
  - Role:    admin (system role)
  - TenantUser + UserRole linking the above
"""

import asyncio
import uuid

import structlog

from app.core.logging import setup_logging
from app.core.security import hash_password
from app.db.session import async_session_factory
from app.modules.identity.models import User
from app.modules.tenancy.models import Permission, Role, Tenant, TenantUser, user_roles

setup_logging()
logger = structlog.get_logger(__name__)

DEMO_TENANT_SLUG = "demo"
ADMIN_EMAIL = "admin@demo.org"
ADMIN_PASSWORD = "Admin123!"
ADMIN_ROLE_CODE = "admin"


async def seed_database() -> None:
    logger.info("Starting database seed")

    async with async_session_factory() as db:
        async with db.begin():
            # ── Tenant ─────────────────────────────────────────────────────────
            from sqlalchemy import select

            existing_tenant = await db.execute(
                select(Tenant).where(Tenant.slug == DEMO_TENANT_SLUG)
            )
            tenant = existing_tenant.scalar_one_or_none()

            if tenant is None:
                tenant = Tenant(
                    id=uuid.uuid4(),
                    slug=DEMO_TENANT_SLUG,
                    name="Demo Organization",
                    type="association",
                    default_language="en",
                )
                db.add(tenant)
                await db.flush()
                logger.info("Created tenant", slug=DEMO_TENANT_SLUG)
            else:
                logger.info("Tenant already exists", slug=DEMO_TENANT_SLUG)

            # ── Permission ─────────────────────────────────────────────────────
            existing_perm = await db.execute(
                select(Permission).where(Permission.code == "admin:all")
            )
            permission = existing_perm.scalar_one_or_none()
            if permission is None:
                permission = Permission(
                    id=uuid.uuid4(),
                    code="admin:all",
                    description="Superadmin permission — full access to all resources",
                )
                db.add(permission)
                await db.flush()

            # ── Role ───────────────────────────────────────────────────────────
            existing_role = await db.execute(
                select(Role).where(
                    Role.tenant_id == tenant.id, Role.code == ADMIN_ROLE_CODE
                )
            )
            role = existing_role.scalar_one_or_none()
            if role is None:
                role = Role(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    code=ADMIN_ROLE_CODE,
                    name="Administrator",
                    description="Full administrative access",
                    is_system_role=True,
                )
                db.add(role)
                await db.flush()
                logger.info("Created role", code=ADMIN_ROLE_CODE)

            # ── User ───────────────────────────────────────────────────────────
            existing_user = await db.execute(
                select(User).where(User.email == ADMIN_EMAIL)
            )
            user = existing_user.scalar_one_or_none()
            if user is None:
                user = User(
                    id=uuid.uuid4(),
                    email=ADMIN_EMAIL,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    display_name="Admin User",
                    status="active",
                )
                db.add(user)
                await db.flush()
                logger.info("Created admin user", email=ADMIN_EMAIL)
            else:
                logger.info("Admin user already exists", email=ADMIN_EMAIL)

            # ── TenantUser ─────────────────────────────────────────────────────
            existing_tu = await db.execute(
                select(TenantUser).where(
                    TenantUser.tenant_id == tenant.id,
                    TenantUser.user_id == user.id,
                )
            )
            tenant_user = existing_tu.scalar_one_or_none()
            if tenant_user is None:
                tenant_user = TenantUser(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    user_id=user.id,
                    profile_type="admin",
                    membership_status="active",
                )
                db.add(tenant_user)
                await db.flush()

            # ── UserRole ───────────────────────────────────────────────────────
            existing_ur = await db.execute(
                select(user_roles).where(
                    user_roles.c.tenant_user_id == tenant_user.id,
                    user_roles.c.role_id == role.id,
                )
            )
            if existing_ur.first() is None:
                await db.execute(
                    user_roles.insert().values(
                        tenant_user_id=tenant_user.id, role_id=role.id
                    )
                )

    logger.info(
        "Seed complete",
        tenant=DEMO_TENANT_SLUG,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
    )


if __name__ == "__main__":
    asyncio.run(seed_database())
