"""
Database seed script — idempotent demo tenant with comprehensive data.

Run once after migrations:
    docker compose exec api python -m app.db.seed

Creates:
  - Tenant:    slug="demo", name="Acme Community Organization"
  - Users:     admin@demo.org, alice@demo.org, bob@demo.org, treasurer@demo.org
  - Roles:     admin (system), member, treasurer
  - Permissions for each role
  - Membership profiles for Alice and Bob
  - Sample documents with versions and chunks (bylaws, meeting minutes)
  - Sample policies (fee policy, attendance policy, code of conduct)
  - Sample contributions and payments
  - Sample disciplinary record
  - Sample events (upcoming and past)
  - Sample announcements (active, expired, and public)

User credentials:
  - admin@demo.org / Admin123!      (Administrator)
  - alice@demo.org / Member123!     (Member)
  - bob@demo.org / Member123!       (Member)
  - treasurer@demo.org / Treasurer123! (Treasurer)
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import structlog

from app.core.logging import setup_logging
from app.core.security import hash_password
from app.db.session import async_session_factory
from app.modules.identity.models import User
from app.modules.tenancy.models import (
    Permission,
    Role,
    Tenant,
    TenantUser,
    role_permissions,
    user_roles,
)
from app.modules.membership.models import MembershipProfile
from app.modules.contributions.models import ContributionRecord, PaymentRecord
from app.modules.policies.models import PolicyRecord
from app.modules.disciplinary.models import DisciplinaryRecord
from app.modules.events.models import Event
from app.modules.announcements.models import Announcement
from app.modules.documents.models import Document, DocumentChunk, DocumentVersion
from app.modules.tenancy.role_catalog import canonical_role_definitions

setup_logging()
logger = structlog.get_logger(__name__)

DEMO_TENANT_SLUG = "demo"

ADMIN_EMAIL = "admin@demo.org"
ADMIN_PASSWORD = "Admin123!"

MEMBER_1_EMAIL = "alice@demo.org"
MEMBER_2_EMAIL = "bob@demo.org"
MEMBER_PASSWORD = "Member123!"

TREASURER_EMAIL = "treasurer@demo.org"
TREASURER_PASSWORD = "Treasurer123!"

ADMIN_ROLE_CODE = "admin"
MEMBER_ROLE_CODE = "member"
TREASURER_ROLE_CODE = "treasurer"
PRINCIPAL_ADMIN_ROLE_CODE = "principal_admin"

NOW = datetime.now(timezone.utc)

PERMISSION_DEFS: list[tuple[str, str]] = [
    ("admin:all", "Superadmin permission — full access to all resources"),
    ("members:read", "Read member profiles"),
    ("members:write", "Create and update member profiles"),
    ("contributions:read", "Read contribution records"),
    ("contributions:write", "Create and update contribution records"),
    ("policies:read", "Read policy documents"),
    ("policies:write", "Create and update policy documents"),
    ("disciplinary:read", "Read disciplinary records"),
    ("disciplinary:write", "Create and update disciplinary records"),
    ("events:read", "Read events"),
    ("events:write", "Create and update events"),
    ("announcements:read", "Read announcements"),
    ("announcements:write", "Create and update announcements"),
    ("documents:read", "Read documents"),
    ("documents:write", "Upload and manage documents"),
]

MEMBER_PERMISSIONS = [
    "members:read",
    "policies:read",
    "events:read",
    "announcements:read",
    "documents:read",
]

TREASURER_PERMISSIONS = [
    "contributions:read",
    "contributions:write",
    "members:read",
]


async def _get_or_create_tenant(db):
    from sqlalchemy import select

    existing = await db.execute(select(Tenant).where(Tenant.slug == DEMO_TENANT_SLUG))
    tenant = existing.scalar_one_or_none()
    if tenant is None:
        tenant = Tenant(
            id=uuid.uuid4(),
            slug=DEMO_TENANT_SLUG,
            name="Acme Community Organization",
            type="association",
            default_language="en",
            branding_json='{"primary_color": "#1f4f8f", "logo_url": ""}',
            settings_json='{"locale": "en", "timezone": "UTC", "modules": {"membership": true, "contributions": true, "policies": true, "disciplinary": true, "events": true, "announcements": true, "chat": true, "notifications": true}}',
        )
        db.add(tenant)
        await db.flush()
        logger.info("Created tenant", slug=DEMO_TENANT_SLUG)
    return tenant


async def _get_or_create_permissions(db) -> dict[str, Permission]:
    from sqlalchemy import select

    perms: dict[str, Permission] = {}
    for code, desc in PERMISSION_DEFS:
        existing = await db.execute(select(Permission).where(Permission.code == code))
        perm = existing.scalar_one_or_none()
        if perm is None:
            perm = Permission(id=uuid.uuid4(), code=code, description=desc)
            db.add(perm)
            await db.flush()
        perms[code] = perm
    return perms


async def _get_or_create_role(db, tenant_id, code, name, description, is_system_role=False):
    from sqlalchemy import select

    existing = await db.execute(
        select(Role).where(Role.tenant_id == tenant_id, Role.code == code)
    )
    role = existing.scalar_one_or_none()
    if role is None:
        role = Role(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            code=code,
            name=name,
            description=description,
            is_system_role=is_system_role,
        )
        db.add(role)
        await db.flush()
        logger.info("Created role", code=code)
    return role


async def _get_or_create_user(db, email, password, display_name):
    from sqlalchemy import select

    existing = await db.execute(select(User).where(User.email == email))
    user = existing.scalar_one_or_none()
    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=hash_password(password),
            display_name=display_name,
            status="active",
        )
        db.add(user)
        await db.flush()
        logger.info("Created user", email=email)
    return user


async def _get_or_create_tenant_user(db, tenant_id, user_id, profile_type, membership_status="active"):
    from sqlalchemy import select

    existing = await db.execute(
        select(TenantUser).where(
            TenantUser.tenant_id == tenant_id,
            TenantUser.user_id == user_id,
        )
    )
    tu = existing.scalar_one_or_none()
    if tu is None:
        tu = TenantUser(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            profile_type=profile_type,
            membership_status=membership_status,
        )
        db.add(tu)
        await db.flush()
    return tu


async def _assign_role_if_not_exists(db, tenant_user_id, role_id):
    from sqlalchemy import select

    existing = await db.execute(
        select(user_roles).where(
            user_roles.c.tenant_user_id == tenant_user_id,
            user_roles.c.role_id == role_id,
        )
    )
    if existing.first() is None:
        await db.execute(
            user_roles.insert().values(tenant_user_id=tenant_user_id, role_id=role_id)
        )


async def _assign_permission_if_not_exists(db, role_id, permission_id):
    from sqlalchemy import select

    existing = await db.execute(
        select(role_permissions).where(
            role_permissions.c.role_id == role_id,
            role_permissions.c.permission_id == permission_id,
        )
    )
    if existing.first() is None:
        await db.execute(
            role_permissions.insert().values(role_id=role_id, permission_id=permission_id)
        )


async def seed_database() -> None:
    logger.info("Starting database seed")

    async with async_session_factory() as db:
        async with db.begin():
            from sqlalchemy import select

            # ── Tenant ─────────────────────────────────────────────────────
            tenant = await _get_or_create_tenant(db)

            # ── Permissions ────────────────────────────────────────────────
            perms = await _get_or_create_permissions(db)

            # ── Roles ──────────────────────────────────────────────────────
            admin_role = await _get_or_create_role(
                db,
                tenant.id,
                ADMIN_ROLE_CODE,
                "Administrator",
                "Full administrative access",
                is_system_role=True,
            )
            canonical_roles: dict[str, Role] = {}
            for definition in canonical_role_definitions():
                canonical_roles[definition.code] = await _get_or_create_role(
                    db,
                    tenant.id,
                    definition.code,
                    definition.name,
                    definition.description,
                    is_system_role=definition.is_system_role,
                )
            member_role = canonical_roles[MEMBER_ROLE_CODE]
            treasurer_role = canonical_roles[TREASURER_ROLE_CODE]
            principal_admin_role = canonical_roles[PRINCIPAL_ADMIN_ROLE_CODE]

            # ── Role-Permission assignments ────────────────────────────────
            await _assign_permission_if_not_exists(db, admin_role.id, perms["admin:all"].id)
            for code in MEMBER_PERMISSIONS:
                await _assign_permission_if_not_exists(db, member_role.id, perms[code].id)
            for code in TREASURER_PERMISSIONS:
                await _assign_permission_if_not_exists(
                    db, treasurer_role.id, perms[code].id
                )

            # ── Users ──────────────────────────────────────────────────────
            admin_user = await _get_or_create_user(db, ADMIN_EMAIL, ADMIN_PASSWORD, "Admin User")
            member_1 = await _get_or_create_user(db, MEMBER_1_EMAIL, MEMBER_PASSWORD, "Alice Johnson")
            member_2 = await _get_or_create_user(db, MEMBER_2_EMAIL, MEMBER_PASSWORD, "Bob Smith")
            treasurer_user = await _get_or_create_user(
                db, TREASURER_EMAIL, TREASURER_PASSWORD, "Carol Williams"
            )

            # ── TenantUser ─────────────────────────────────────────────────
            admin_tu = await _get_or_create_tenant_user(db, tenant.id, admin_user.id, "admin")
            member_1_tu = await _get_or_create_tenant_user(db, tenant.id, member_1.id, "member")
            member_2_tu = await _get_or_create_tenant_user(db, tenant.id, member_2.id, "member")
            treasurer_tu = await _get_or_create_tenant_user(
                db, tenant.id, treasurer_user.id, "staff"
            )

            # ── UserRole assignments ───────────────────────────────────────
            await _assign_role_if_not_exists(db, admin_tu.id, admin_role.id)
            await _assign_role_if_not_exists(db, admin_tu.id, principal_admin_role.id)
            await _assign_role_if_not_exists(db, member_1_tu.id, member_role.id)
            await _assign_role_if_not_exists(db, member_2_tu.id, member_role.id)
            await _assign_role_if_not_exists(db, treasurer_tu.id, treasurer_role.id)
            await _assign_role_if_not_exists(db, treasurer_tu.id, member_role.id)

            # ── Membership Profiles ────────────────────────────────────────
            member_defs = [
                (member_1, MEMBER_1_EMAIL, "MEM-001", "Alice", "Johnson", "+1-555-0101",
                 '{"department": "events"}'),
                (member_2, MEMBER_2_EMAIL, "MEM-002", "Bob", "Smith", "+1-555-0102", "{}"),
            ]
            for user_obj, email, code, first, last, phone, meta in member_defs:
                existing = await db.execute(
                    select(MembershipProfile).where(
                        MembershipProfile.tenant_id == tenant.id,
                        MembershipProfile.member_code == code,
                    )
                )
                if existing.scalar_one_or_none() is None:
                    mp = MembershipProfile(
                        id=uuid.uuid4(),
                        tenant_id=tenant.id,
                        user_id=user_obj.id,
                        member_code=code,
                        first_name=first,
                        last_name=last,
                        display_name=f"{first} {last}",
                        email=email,
                        phone=phone,
                        status="active",
                        metadata_json=meta,
                    )
                    db.add(mp)
                    await db.flush()

            # Fetch all profiles for downstream use
            result = await db.execute(
                select(MembershipProfile).where(MembershipProfile.tenant_id == tenant.id)
            )
            profiles: dict[str, MembershipProfile] = {
                p.email: p for p in result.scalars().all() if p.email
            }

            # ── Documents with Versions and Chunks ─────────────────────────
            doc_defs = [
                (
                    "Community Association Bylaws",
                    "Official bylaws governing the community association",
                    "members_only",
                    [
                        "The association shall have a Board of Directors consisting of 7 "
                        "members elected by the general assembly for a term of 2 years.",
                        "Annual membership fees shall be determined by the Board of Directors "
                        "and ratified by the general assembly at the annual general meeting.",
                        "All members in good standing are eligible to vote at the general "
                        "assembly. A member is in good standing if all fees are paid and no "
                        "disciplinary sanctions are pending.",
                        "The Board of Directors shall meet at least once per quarter. Special "
                        "meetings may be called by the President or by a majority of the Board.",
                        "Amendments to these bylaws require a two-thirds majority vote of the "
                        "members present at the annual general meeting, provided that notice of "
                        "the proposed amendment was given at least 30 days in advance.",
                    ],
                ),
                (
                    "Meeting Minutes - Q1 2026",
                    "Minutes from the first quarter board meeting",
                    "members_only",
                    [
                        "The Q1 2026 board meeting was held on January 15, 2026. Present: "
                        "President Alice Johnson, Treasurer Carol Williams, Secretary Bob Smith.",
                        "The treasurer reported that the association has a current balance of "
                        "$12,450. Annual membership fee collection is at 72% of target.",
                        "The board approved a budget of $3,500 for the annual summer barbecue "
                        "event, scheduled for July 2026.",
                        "A motion to update the parking policy was tabled until the Q2 meeting "
                        "pending further community input.",
                    ],
                ),
            ]
            for title, desc, access_scope, chunks_text in doc_defs:
                existing = await db.execute(
                    select(Document).where(
                        Document.tenant_id == tenant.id,
                        Document.title == title,
                    )
                )
                if existing.scalar_one_or_none() is not None:
                    continue

                doc = Document(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    title=title,
                    description=desc,
                    source_type="upload",
                    language="en",
                    access_scope=access_scope,
                    status="ready",
                    created_by=admin_user.id,
                )
                db.add(doc)
                await db.flush()

                version = DocumentVersion(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    document_id=doc.id,
                    version_number=1,
                    file_name=f"{title.lower().replace(' ', '-')}-2026.pdf",
                    mime_type="application/pdf",
                    file_size_bytes=len(" ".join(chunks_text).encode("utf-8")),
                    storage_bucket="documents",
                    storage_key=f"{tenant.id}/{doc.id}/v1/document.pdf",
                    checksum=uuid.uuid4().hex,
                    created_by=admin_user.id,
                )
                db.add(version)
                await db.flush()

                doc.current_version_id = version.id

                for i, text in enumerate(chunks_text):
                    chunk = DocumentChunk(
                        id=uuid.uuid4(),
                        tenant_id=tenant.id,
                        document_id=doc.id,
                        document_version_id=version.id,
                        chunk_index=i,
                        text=text,
                        language="en",
                        token_count=len(text.split()),
                    )
                    db.add(chunk)
                await db.flush()
                logger.info("Created document", title=title)

            # Fetch document IDs for policy linking
            doc_result = await db.execute(
                select(Document).where(Document.tenant_id == tenant.id)
            )
            docs_by_title = {d.title: d for d in doc_result.scalars().all()}
            bylaws_doc = docs_by_title.get("Community Association Bylaws")

            # ── Policies ───────────────────────────────────────────────────
            policy_defs = [
                (
                    "Annual Membership Fee Policy",
                    "financial",
                    "Annual membership fees are due by January 31 each year. Late payments "
                    "incur a $25 penalty. Members with unpaid fees beyond 90 days may have "
                    "their voting rights suspended.",
                    bylaws_doc.id if bylaws_doc else None,
                ),
                (
                    "Meeting Attendance Policy",
                    "governance",
                    "Members are expected to attend at least 50% of general assemblies per "
                    "year. Unexcused absences may result in a written warning after three "
                    "consecutive missed meetings.",
                    None,
                ),
                (
                    "Code of Conduct",
                    "conduct",
                    "All members shall treat fellow members with respect. Harassment, "
                    "discrimination, or disruptive behavior at association events may result "
                    "in disciplinary action including suspension or expulsion.",
                    None,
                ),
            ]
            for title, category, description, doc_id in policy_defs:
                existing = await db.execute(
                    select(PolicyRecord).where(
                        PolicyRecord.tenant_id == tenant.id,
                        PolicyRecord.title == title,
                    )
                )
                if existing.scalar_one_or_none() is not None:
                    continue

                policy = PolicyRecord(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    title=title,
                    category=category,
                    description=description,
                    document_id=doc_id,
                    status="published",
                    created_by=admin_user.id,
                )
                db.add(policy)
                await db.flush()
                logger.info("Created policy", title=title)

            # ── Contributions and Payments ─────────────────────────────────
            alice_profile = profiles.get(MEMBER_1_EMAIL)
            bob_profile = profiles.get(MEMBER_2_EMAIL)

            existing_contrib = await db.execute(
                select(ContributionRecord).where(
                    ContributionRecord.tenant_id == tenant.id,
                    ContributionRecord.year == 2026,
                )
            )
            if existing_contrib.scalar_one_or_none() is None:
                if alice_profile:
                    contrib1 = ContributionRecord(
                        id=uuid.uuid4(),
                        tenant_id=tenant.id,
                        membership_profile_id=alice_profile.id,
                        year=2026,
                        expected_amount=150.00,
                        paid_amount=100.00,
                        balance=50.00,
                        currency="EUR",
                        status="partial",
                        due_date=NOW.replace(month=1, day=31, hour=23, minute=59),
                    )
                    db.add(contrib1)
                    await db.flush()

                    payment = PaymentRecord(
                        id=uuid.uuid4(),
                        tenant_id=tenant.id,
                        contribution_record_id=contrib1.id,
                        amount=100.00,
                        currency="EUR",
                        paid_at=NOW.replace(month=1, day=15),
                        payment_method="bank_transfer",
                        reference="TRF-2026-001",
                        recorded_by=treasurer_user.id,
                    )
                    db.add(payment)

                if bob_profile:
                    contrib2 = ContributionRecord(
                        id=uuid.uuid4(),
                        tenant_id=tenant.id,
                        membership_profile_id=bob_profile.id,
                        year=2026,
                        expected_amount=150.00,
                        paid_amount=0.00,
                        balance=150.00,
                        currency="EUR",
                        status="pending",
                        due_date=NOW.replace(month=1, day=31, hour=23, minute=59),
                    )
                    db.add(contrib2)

                await db.flush()
                logger.info("Created contributions and payments")

            # ── Disciplinary Records ───────────────────────────────────────
            existing_disc = await db.execute(
                select(DisciplinaryRecord).where(
                    DisciplinaryRecord.tenant_id == tenant.id,
                    DisciplinaryRecord.title == "Late fee - missed AGM",
                )
            )
            if existing_disc.scalar_one_or_none() is None and bob_profile is not None:
                # Find attendance policy for linking
                pol_result = await db.execute(
                    select(PolicyRecord).where(
                        PolicyRecord.tenant_id == tenant.id,
                        PolicyRecord.title == "Meeting Attendance Policy",
                    )
                )
                attendance_policy = pol_result.scalar_one_or_none()

                disc = DisciplinaryRecord(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    membership_profile_id=bob_profile.id,
                    policy_record_id=attendance_policy.id if attendance_policy else None,
                    title="Late fee - missed AGM",
                    description="Bob Smith missed the Annual General Meeting on March 1, "
                    "2026 without prior notice. A $25 late fee has been applied "
                    "per the attendance policy.",
                    amount=25.00,
                    currency="EUR",
                    status="open",
                    recorded_by=admin_user.id,
                )
                db.add(disc)
                await db.flush()
                logger.info("Created disciplinary record")

            # ── Events ─────────────────────────────────────────────────────
            event_defs = [
                (
                    "Annual General Meeting 2026",
                    "The annual general meeting for all members. Agenda includes budget "
                    "approval, board elections, and policy updates.",
                    NOW + timedelta(days=30),
                    NOW + timedelta(days=30, hours=3),
                    "Community Center, Main Hall",
                    "members_only",
                    "published",
                ),
                (
                    "Summer BBQ 2026",
                    "Annual summer barbecue for members and their families. Food and "
                    "drinks provided. RSVP required.",
                    NOW + timedelta(days=60),
                    NOW + timedelta(days=60, hours=5),
                    "Riverside Park, Pavilion 3",
                    "members_only",
                    "published",
                ),
                (
                    "Board Meeting - Q2 2026",
                    "Regular quarterly board meeting. Board members only.",
                    NOW + timedelta(days=14),
                    NOW + timedelta(days=14, hours=2),
                    "Board Room, Building A",
                    "role_restricted",
                    "published",
                ),
                (
                    "New Member Orientation",
                    "Welcome session for new members joining the association.",
                    NOW - timedelta(days=15),
                    NOW - timedelta(days=15, hours=2),
                    "Community Center, Room 2",
                    "members_only",
                    "completed",
                ),
            ]
            for title, desc, start, end, location, visibility, status in event_defs:
                existing = await db.execute(
                    select(Event).where(
                        Event.tenant_id == tenant.id,
                        Event.title == title,
                    )
                )
                if existing.scalar_one_or_none() is not None:
                    continue

                event = Event(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    title=title,
                    description=desc,
                    start_at=start,
                    end_at=end,
                    location=location,
                    visibility_scope=visibility,
                    status=status,
                    created_by=admin_user.id,
                )
                db.add(event)
                await db.flush()
                logger.info("Created event", title=title)

            # ── Announcements ──────────────────────────────────────────────
            ann_defs = [
                (
                    "Welcome to 2026!",
                    "Happy New Year to all members! The board wishes everyone a great year "
                    "ahead. Annual membership fees are now due. Please log in to your profile "
                    "to check your balance and make a payment.",
                    "members_only",
                    NOW - timedelta(days=10),
                    NOW + timedelta(days=30),
                ),
                (
                    "Summer BBQ - Save the Date",
                    "Mark your calendars! The annual Summer BBQ will be held on July 18, "
                    "2026 at Riverside Park. More details to follow soon.",
                    "members_only",
                    NOW - timedelta(days=5),
                    NOW + timedelta(days=60),
                ),
                (
                    "Office Closure - Holidays",
                    "The association office will be closed from December 24 to January 1 "
                    "for the holiday season.",
                    "members_only",
                    NOW - timedelta(days=120),
                    NOW - timedelta(days=90),
                ),
                (
                    "Parking Lot Renovation",
                    "The main parking lot will be under renovation from March 15 to March "
                    "20. Please use the overflow parking lot on Elm Street during this period.",
                    "tenant_public",
                    NOW - timedelta(days=2),
                    NOW + timedelta(days=25),
                ),
            ]
            for title, body, visibility, published_at, expires_at in ann_defs:
                existing = await db.execute(
                    select(Announcement).where(
                        Announcement.tenant_id == tenant.id,
                        Announcement.title == title,
                    )
                )
                if existing.scalar_one_or_none() is not None:
                    continue

                ann = Announcement(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    title=title,
                    body=body,
                    visibility_scope=visibility,
                    published_at=published_at,
                    expires_at=expires_at,
                    created_by=admin_user.id,
                )
                db.add(ann)
                await db.flush()
                logger.info("Created announcement", title=title)

    logger.info(
        "Seed complete",
        tenant=DEMO_TENANT_SLUG,
        admin_email=ADMIN_EMAIL,
        admin_password=ADMIN_PASSWORD,
        member_password=MEMBER_PASSWORD,
        treasurer_email=TREASURER_EMAIL,
        treasurer_password=TREASURER_PASSWORD,
    )


if __name__ == "__main__":
    asyncio.run(seed_database())
