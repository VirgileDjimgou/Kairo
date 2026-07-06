"""
Multi-tenant demo provisioning helper.

This module complements the base demo seed by adding a second organization and
a cross-tenant demo user so the tenant picker and switcher can be exercised in a
real local stack without inventing cross-tenant administration.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select

from app.core.logging import setup_logging
from app.db.session import async_session_factory
from app.modules.announcements.models import Announcement
from app.modules.contributions.models import ContributionRecord
from app.modules.events.models import Event
from app.modules.identity.models import User
from app.modules.membership.models import MembershipProfile
from app.modules.tenancy.models import Role, Tenant, user_roles
from app.modules.tenancy.role_catalog import canonical_role_definitions

from app.db import seed as base_seed

setup_logging()
logger = structlog.get_logger(__name__)

SECONDARY_TENANT_SLUG = "riverdale"
SECONDARY_TENANT_NAME = "Riverdale Sports Union"
SECONDARY_BRANDING = {"primary_color": "#2f6f55", "logo_url": ""}
SECONDARY_SETTINGS = {
    "locale": "en",
    "timezone": "UTC",
    "modules": {
        "membership": True,
        "contributions": True,
        "policies": True,
        "disciplinary": True,
        "events": True,
        "announcements": True,
        "chat": True,
        "notifications": True,
    },
}

MULTI_TENANT_EMAIL = "switcher@demo.org"
MULTI_TENANT_PASSWORD = "Switcher123!"
SECONDARY_ADMIN_EMAIL = "riverdale-admin@demo.org"
SECONDARY_ADMIN_PASSWORD = "RiverdaleAdmin123!"


async def _get_or_create_tenant(db, slug: str, name: str, *, branding: dict, settings: dict) -> Tenant:
    existing = await db.execute(select(Tenant).where(Tenant.slug == slug))
    tenant = existing.scalar_one_or_none()
    if tenant is None:
        tenant = Tenant(
            id=uuid.uuid4(),
            slug=slug,
            name=name,
            type="association",
            default_language="en",
            branding_json=json.dumps(branding),
            settings_json=json.dumps(settings),
        )
        db.add(tenant)
        await db.flush()
        logger.info("Created secondary tenant", slug=slug)
    return tenant


async def _get_or_create_user(db, email: str, password: str, display_name: str) -> User:
    existing = await db.execute(select(User).where(User.email == email))
    user = existing.scalar_one_or_none()
    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=base_seed.hash_password(password),
            display_name=display_name,
            status="active",
        )
        db.add(user)
        await db.flush()
        logger.info("Created multi-tenant demo user", email=email)
    return user


async def _get_or_create_profile(
    db,
    *,
    tenant_id,
    user_id,
    member_code: str,
    first_name: str,
    last_name: str,
    display_name: str,
    email: str,
) -> MembershipProfile:
    existing = await db.execute(
        select(MembershipProfile).where(
            MembershipProfile.tenant_id == tenant_id,
            MembershipProfile.user_id == user_id,
        )
    )
    profile = existing.scalar_one_or_none()
    if profile is None:
        profile = MembershipProfile(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            member_code=member_code,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            email=email,
            status="active",
        )
        db.add(profile)
        await db.flush()
    return profile


async def seed_multi_tenant_demo() -> None:
    logger.info("Starting multi-tenant demo provisioning")
    await base_seed.seed_database()

    async with async_session_factory() as db:
        async with db.begin():
            demo_tenant = await db.scalar(select(Tenant).where(Tenant.slug == base_seed.DEMO_TENANT_SLUG))
            if demo_tenant is None:
                raise RuntimeError("Base demo tenant is missing. Run the main seed first.")

            secondary_tenant = await _get_or_create_tenant(
                db,
                SECONDARY_TENANT_SLUG,
                SECONDARY_TENANT_NAME,
                branding=SECONDARY_BRANDING,
                settings=SECONDARY_SETTINGS,
            )

            perms = await base_seed._get_or_create_permissions(db)

            admin_role = await base_seed._get_or_create_role(
                db,
                secondary_tenant.id,
                base_seed.ADMIN_ROLE_CODE,
                "Administrator",
                "Full administrative access",
                is_system_role=True,
            )
            canonical_roles: dict[str, Role] = {}
            for definition in canonical_role_definitions():
                canonical_roles[definition.code] = await base_seed._get_or_create_role(
                    db,
                    secondary_tenant.id,
                    definition.code,
                    definition.name,
                    definition.description,
                    is_system_role=definition.is_system_role,
                )

            await base_seed._assign_permission_if_not_exists(db, admin_role.id, perms["admin:all"].id)
            for code in base_seed.MEMBER_PERMISSIONS:
                await base_seed._assign_permission_if_not_exists(db, canonical_roles["member"].id, perms[code].id)
            for code in base_seed.TREASURER_PERMISSIONS:
                await base_seed._assign_permission_if_not_exists(db, canonical_roles["treasurer"].id, perms[code].id)

            switcher_user = await _get_or_create_user(
                db,
                MULTI_TENANT_EMAIL,
                MULTI_TENANT_PASSWORD,
                "Multi Tenant Switcher",
            )
            secondary_admin = await _get_or_create_user(
                db,
                SECONDARY_ADMIN_EMAIL,
                SECONDARY_ADMIN_PASSWORD,
                "Riverdale Admin",
            )

            await base_seed._get_or_create_tenant_user(
                db,
                demo_tenant.id,
                switcher_user.id,
                "member",
            )
            secondary_membership = await base_seed._get_or_create_tenant_user(
                db,
                secondary_tenant.id,
                switcher_user.id,
                "member",
            )
            secondary_admin_membership = await base_seed._get_or_create_tenant_user(
                db,
                secondary_tenant.id,
                secondary_admin.id,
                "admin",
            )

            await base_seed._assign_role_if_not_exists(db, demo_membership.id, canonical_roles["member"].id)
            await base_seed._assign_role_if_not_exists(db, secondary_membership.id, canonical_roles["member"].id)
            await base_seed._assign_role_if_not_exists(db, secondary_admin_membership.id, admin_role.id)
            await base_seed._assign_role_if_not_exists(db, secondary_admin_membership.id, canonical_roles["principal_admin"].id)

            demo_profile = await _get_or_create_profile(
                db,
                tenant_id=demo_tenant.id,
                user_id=switcher_user.id,
                member_code="MT-001",
                first_name="Multi",
                last_name="Tenant",
                display_name="Multi Tenant Switcher",
                email=MULTI_TENANT_EMAIL,
            )
            secondary_profile = await _get_or_create_profile(
                db,
                tenant_id=secondary_tenant.id,
                user_id=switcher_user.id,
                member_code="RV-001",
                first_name="Multi",
                last_name="Tenant",
                display_name="Multi Tenant Switcher",
                email=MULTI_TENANT_EMAIL,
            )

            now = datetime.now(timezone.utc)
            demo_contrib = await db.scalar(
                select(ContributionRecord).where(
                    ContributionRecord.tenant_id == demo_tenant.id,
                    ContributionRecord.membership_profile_id == demo_profile.id,
                    ContributionRecord.year == 2026,
                )
            )
            if demo_contrib is None:
                demo_contrib = ContributionRecord(
                    id=uuid.uuid4(),
                    tenant_id=demo_tenant.id,
                    membership_profile_id=demo_profile.id,
                    year=2026,
                    expected_amount="120.00",
                    paid_amount="45.00",
                    balance="75.00",
                    currency="EUR",
                    status="partial",
                    due_date=now + timedelta(days=30),
                    metadata_json="{}",
                )
                db.add(demo_contrib)

            secondary_contrib = await db.scalar(
                select(ContributionRecord).where(
                    ContributionRecord.tenant_id == secondary_tenant.id,
                    ContributionRecord.membership_profile_id == secondary_profile.id,
                    ContributionRecord.year == 2026,
                )
            )
            if secondary_contrib is None:
                secondary_contrib = ContributionRecord(
                    id=uuid.uuid4(),
                    tenant_id=secondary_tenant.id,
                    membership_profile_id=secondary_profile.id,
                    year=2026,
                    expected_amount="80.00",
                    paid_amount="80.00",
                    balance="0.00",
                    currency="EUR",
                    status="paid",
                    due_date=now + timedelta(days=30),
                    metadata_json="{}",
                )
                db.add(secondary_contrib)

            if not await db.scalar(
                select(Event).where(
                    Event.tenant_id == secondary_tenant.id,
                    Event.title == "Riverdale Welcome Meeting",
                )
            ):
                db.add(
                    Event(
                        id=uuid.uuid4(),
                        tenant_id=secondary_tenant.id,
                        title="Riverdale Welcome Meeting",
                        description="Introductory meeting for the second tenant demo.",
                        start_at=now + timedelta(days=7),
                        end_at=now + timedelta(days=7, hours=2),
                        location="Riverdale Clubhouse",
                        visibility_scope="members_only",
                        status="published",
                        created_by=secondary_admin.id,
                        metadata_json=json.dumps({"demo": "multi-tenant"}),
                    )
                )

            if not await db.scalar(
                select(Announcement).where(
                    Announcement.tenant_id == secondary_tenant.id,
                    Announcement.title == "Riverdale onboarding note",
                )
            ):
                db.add(
                    Announcement(
                        id=uuid.uuid4(),
                        tenant_id=secondary_tenant.id,
                        title="Riverdale onboarding note",
                        body="This second tenant demonstrates the tenant picker and tenant switcher.",
                        visibility_scope="tenant_public",
                        status="published",
                        published_at=now,
                        created_by=secondary_admin.id,
                    )
                )

        await db.commit()

    logger.info(
        "Multi-tenant demo provisioning complete",
        secondary_tenant=SECONDARY_TENANT_SLUG,
        switcher_email=MULTI_TENANT_EMAIL,
        admin_email=SECONDARY_ADMIN_EMAIL,
    )


if __name__ == "__main__":
    asyncio.run(seed_multi_tenant_demo())
