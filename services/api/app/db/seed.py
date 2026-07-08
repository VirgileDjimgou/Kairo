"""
Database seed script — idempotent demo tenant with comprehensive data.

Run once after migrations:
    docker compose exec api python -m app.db.seed

Creates:
  - Tenant:    slug="demo", name="Combis Sport Verein"
  - Users:     admin@demo.org, alice@demo.org, bob@demo.org, treasurer@demo.org,
               secretary@demo.org, auditor@demo.org, censor@demo.org,
               sports@demo.org, president@demo.org, vice-president@demo.org,
               principal@demo.org
  - Roles:     admin (system), member, treasurer, secretary_general, auditor,
               censor, sports_manager, president, vice_president, principal_admin
  - Permissions for each role
  - Membership profiles for the core demo accounts plus a larger fictional member roster
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
  - secretary@demo.org / Secretary123! (Secretary General)
  - auditor@demo.org / Auditor123!     (Auditor)
  - censor@demo.org / Censor123!       (Censor)
  - sports@demo.org / Sports123!       (Sports Manager)
  - president@demo.org / President123! (President)
  - vice-president@demo.org / VicePresident123! (Vice President)
  - principal@demo.org / Principal123! (Principal Admin)
"""

import asyncio
import json
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

SECRETARY_EMAIL = "secretary@demo.org"
SECRETARY_PASSWORD = "Secretary123!"

AUDITOR_EMAIL = "auditor@demo.org"
AUDITOR_PASSWORD = "Auditor123!"

CENSOR_EMAIL = "censor@demo.org"
CENSOR_PASSWORD = "Censor123!"

SPORTS_EMAIL = "sports@demo.org"
SPORTS_PASSWORD = "Sports123!"

PRESIDENT_EMAIL = "president@demo.org"
PRESIDENT_PASSWORD = "President123!"

VICE_PRESIDENT_EMAIL = "vice-president@demo.org"
VICE_PRESIDENT_PASSWORD = "VicePresident123!"

PRINCIPAL_ADMIN_EMAIL = "principal@demo.org"
PRINCIPAL_ADMIN_PASSWORD = "Principal123!"

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
            name="Combis Sport Verein",
            type="association",
            default_language="fr",
            branding_json='{"primary_color": "#1f4f8f", "logo_url": ""}',
            settings_json='{"locale": "fr", "timezone": "Europe/Berlin", "modules": {"membership": true, "contributions": true, "policies": true, "disciplinary": true, "events": true, "announcements": true, "chat": true, "notifications": true}}',
        )
        db.add(tenant)
        await db.flush()
        logger.info("Created tenant", slug=DEMO_TENANT_SLUG)
    else:
        tenant.name = "Combis Sport Verein"
        tenant.default_language = "fr"
        tenant.branding_json = '{"primary_color": "#1f4f8f", "logo_url": ""}'
        tenant.settings_json = '{"locale": "fr", "timezone": "Europe/Berlin", "modules": {"membership": true, "contributions": true, "policies": true, "disciplinary": true, "events": true, "announcements": true, "chat": true, "notifications": true}}'
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


async def _get_or_create_user(db, email, password, display_name, preferred_language="fr"):
    from sqlalchemy import select

    existing = await db.execute(select(User).where(User.email == email))
    user = existing.scalar_one_or_none()
    if user is None:
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=hash_password(password),
            display_name=display_name,
            preferred_language=preferred_language,
            status="active",
        )
        db.add(user)
        await db.flush()
        logger.info("Created user", email=email)
    else:
        user.display_name = display_name
        user.preferred_language = preferred_language
    return user


def _email_local(first_name: str, last_name: str) -> str:
    return f"{first_name.lower()}.{last_name.lower()}".replace(" ", "-")


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
            admin_user = await _get_or_create_user(db, ADMIN_EMAIL, ADMIN_PASSWORD, "Claude Mvondo")
            member_1 = await _get_or_create_user(db, MEMBER_1_EMAIL, MEMBER_PASSWORD, "Aline Ndzi")
            member_2 = await _get_or_create_user(db, MEMBER_2_EMAIL, MEMBER_PASSWORD, "Boris Schneider")
            treasurer_user = await _get_or_create_user(
                db, TREASURER_EMAIL, TREASURER_PASSWORD, "Heike Schneider"
            )
            secretary_user = await _get_or_create_user(
                db, SECRETARY_EMAIL, SECRETARY_PASSWORD, "Mireille Tchoumi"
            )
            auditor_user = await _get_or_create_user(
                db, AUDITOR_EMAIL, AUDITOR_PASSWORD, "Markus Weber"
            )
            censor_user = await _get_or_create_user(
                db, CENSOR_EMAIL, CENSOR_PASSWORD, "Arlette Ndzi"
            )
            sports_user = await _get_or_create_user(
                db, SPORTS_EMAIL, SPORTS_PASSWORD, "Pascal Nsame"
            )
            president_user = await _get_or_create_user(
                db, PRESIDENT_EMAIL, PRESIDENT_PASSWORD, "Jean-Paul Fouda"
            )
            vice_president_user = await _get_or_create_user(
                db, VICE_PRESIDENT_EMAIL, VICE_PRESIDENT_PASSWORD, "Sabine Keller"
            )
            principal_admin_user = await _get_or_create_user(
                db, PRINCIPAL_ADMIN_EMAIL, PRINCIPAL_ADMIN_PASSWORD, "Thomas Becker"
            )

            extra_member_name_defs = [
                ("Cedric", "Nkoum"), ("Brigitte", "Essomba"), ("Patrick", "Mbarga"), ("Estelle", "Nana"),
                ("Roger", "Tchana"), ("Solange", "Mbianda"), ("Armand", "Fouelefack"), ("Nadine", "Kemta"),
                ("Blaise", "Moukoko"), ("Micheline", "Ngassam"), ("Wilfried", "Ngono"), ("Carine", "Tchounga"),
                ("Jonas", "Mebenga"), ("Diane", "Minko"), ("Kevin", "Abega"), ("Prisca", "Moundi"),
                ("Lukas", "Schneider"), ("Anna", "Mueller"), ("Jonas", "Weber"), ("Leonie", "Fischer"),
                ("Felix", "Wagner"), ("Sophie", "Becker"), ("Tim", "Hoffmann"), ("Clara", "Schulz"),
                ("Paul", "Richter"), ("Mia", "Klein"), ("Jan", "Hartmann"), ("Laura", "Zimmermann"),
                ("Noah", "Krause"), ("Emma", "Krueger"), ("David", "Wolf"), ("Hannah", "Neumann"),
                ("Simon", "Braun"), ("Lisa", "Werner"), ("Nico", "Schmid"), ("Julia", "Schubert"),
            ]
            extra_member_users: list[tuple[User, str, str, str]] = []
            for first_name, last_name in extra_member_name_defs:
                email = f"{_email_local(first_name, last_name)}@combis-demo.org"
                display_name = f"{first_name} {last_name}"
                user = await _get_or_create_user(
                    db,
                    email,
                    MEMBER_PASSWORD,
                    display_name,
                )
                extra_member_users.append((user, email, first_name, last_name))

            # ── TenantUser ─────────────────────────────────────────────────
            admin_tu = await _get_or_create_tenant_user(db, tenant.id, admin_user.id, "admin")
            member_1_tu = await _get_or_create_tenant_user(db, tenant.id, member_1.id, "member")
            member_2_tu = await _get_or_create_tenant_user(db, tenant.id, member_2.id, "member")
            treasurer_tu = await _get_or_create_tenant_user(
                db, tenant.id, treasurer_user.id, "staff"
            )
            secretary_tu = await _get_or_create_tenant_user(
                db, tenant.id, secretary_user.id, "staff"
            )
            auditor_tu = await _get_or_create_tenant_user(
                db, tenant.id, auditor_user.id, "staff"
            )
            censor_tu = await _get_or_create_tenant_user(db, tenant.id, censor_user.id, "staff")
            sports_tu = await _get_or_create_tenant_user(db, tenant.id, sports_user.id, "staff")
            president_tu = await _get_or_create_tenant_user(
                db, tenant.id, president_user.id, "staff"
            )
            vice_president_tu = await _get_or_create_tenant_user(
                db, tenant.id, vice_president_user.id, "staff"
            )
            principal_admin_tu = await _get_or_create_tenant_user(
                db, tenant.id, principal_admin_user.id, "admin"
            )
            extra_member_tus = []
            for user, _, _, _ in extra_member_users:
                extra_member_tus.append(
                    await _get_or_create_tenant_user(db, tenant.id, user.id, "member")
                )

            # ── UserRole assignments ───────────────────────────────────────
            await _assign_role_if_not_exists(db, admin_tu.id, admin_role.id)
            await _assign_role_if_not_exists(db, admin_tu.id, principal_admin_role.id)
            await _assign_role_if_not_exists(db, member_1_tu.id, member_role.id)
            await _assign_role_if_not_exists(db, member_2_tu.id, member_role.id)
            await _assign_role_if_not_exists(db, treasurer_tu.id, treasurer_role.id)
            await _assign_role_if_not_exists(db, treasurer_tu.id, member_role.id)
            await _assign_role_if_not_exists(db, secretary_tu.id, canonical_roles["secretary_general"].id)
            await _assign_role_if_not_exists(db, auditor_tu.id, canonical_roles["auditor"].id)
            await _assign_role_if_not_exists(db, censor_tu.id, canonical_roles["censor"].id)
            await _assign_role_if_not_exists(db, sports_tu.id, canonical_roles["sports_manager"].id)
            await _assign_role_if_not_exists(db, president_tu.id, canonical_roles["president"].id)
            await _assign_role_if_not_exists(
                db, vice_president_tu.id, canonical_roles["vice_president"].id
            )
            await _assign_role_if_not_exists(
                db, principal_admin_tu.id, principal_admin_role.id
            )
            for tenant_user in extra_member_tus:
                await _assign_role_if_not_exists(db, tenant_user.id, member_role.id)

            # ── Membership Profiles ────────────────────────────────────────
            member_defs = [
                (member_1, MEMBER_1_EMAIL, "MEM-001", "Aline", "Ndzi", "+49-151-0101",
                 '{"department": "events"}'),
                (member_2, MEMBER_2_EMAIL, "MEM-002", "Boris", "Schneider", "+49-151-0102", "{}"),
                (treasurer_user, TREASURER_EMAIL, "TRE-001", "Heike", "Schneider", None, "{}"),
                (secretary_user, SECRETARY_EMAIL, "SEC-001", "Mireille", "Tchoumi", None, "{}"),
                (auditor_user, AUDITOR_EMAIL, "AUD-001", "Markus", "Weber", None, "{}"),
                (censor_user, CENSOR_EMAIL, "CEN-001", "Arlette", "Ndzi", None, "{}"),
                (sports_user, SPORTS_EMAIL, "SPT-001", "Pascal", "Nsame", None, "{}"),
                (president_user, PRESIDENT_EMAIL, "PRE-001", "Jean-Paul", "Fouda", None, "{}"),
                (
                    vice_president_user,
                    VICE_PRESIDENT_EMAIL,
                    "VPR-001",
                    "Sabine",
                    "Keller",
                    None,
                    "{}",
                ),
                (
                    principal_admin_user,
                    PRINCIPAL_ADMIN_EMAIL,
                    "PAD-001",
                    "Thomas",
                    "Becker",
                    None,
                    "{}",
                ),
            ]
            for index, (user_obj, email, first_name, last_name) in enumerate(extra_member_users, start=3):
                member_defs.append(
                    (
                        user_obj,
                        email,
                        f"MEM-{index:03d}",
                        first_name,
                        last_name,
                        None,
                        "{}",
                    )
                )
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
                    "Statuts Combis Sport Verein (FR)",
                    "Version française des statuts et règles de gouvernance de l'association",
                    "members_only",
                    "fr",
                    [
                        "Combis Sport Verein est une association sportive et communautaire. "
                        "Le bureau comprend le président, le vice-président, le secrétaire général, "
                        "le trésorier, le censeur et le commissaire aux comptes.",
                        "Les cotisations annuelles sont validées en assemblée générale. Un membre "
                        "est considéré à jour lorsqu'il a réglé sa cotisation annuelle et ne fait "
                        "pas l'objet d'une suspension disciplinaire active.",
                        "Les assemblées générales ordinaires ont lieu au moins une fois par an. "
                        "Les convocations doivent être communiquées au moins trente jours à l'avance.",
                        "Les documents officiels de fonctionnement, les annonces générales et les "
                        "règles sportives peuvent être consultés par l'ensemble des membres.",
                    ],
                ),
                (
                    "Combis Sport Verein Bylaws (EN)",
                    "English reference version of the association bylaws",
                    "members_only",
                    "en",
                    [
                        "Combis Sport Verein operates as a sports and mutual-support association. "
                        "Its office roles include president, vice president, secretary general, "
                        "treasurer, censor, and auditor.",
                        "Annual contributions are approved by the general assembly. A member in "
                        "good standing has paid the current annual fee and is not under an active sanction.",
                        "Official governance notices must be communicated in advance and remain "
                        "available to members through the organization workspace.",
                        "The principal administrator manages platform configuration but does not "
                        "override tenant isolation or backend authorization rules.",
                    ],
                ),
                (
                    "Satzung Combis Sport Verein (DE)",
                    "Deutsche Referenzfassung der Satzung und Vereinsordnung",
                    "members_only",
                    "de",
                    [
                        "Combis Sport Verein ist ein Sport- und Gemeinschaftsverein. "
                        "Zum Vorstand gehoeren Praesident, Vizepraesident, Generalsekretaer, "
                        "Schatzmeister, Zensor und Kassenpruefer.",
                        "Jahresbeitraege werden in der Mitgliederversammlung bestaetigt. "
                        "Ein Mitglied gilt als ordnungsgemaess, wenn der Beitrag bezahlt ist "
                        "und keine aktive disziplinarische Sperre besteht.",
                        "Offizielle Vereinsdokumente, allgemeine Mitteilungen und Sportordnungen "
                        "stehen allen Mitgliedern im dafuer vorgesehenen Bereich zur Verfuegung.",
                    ],
                ),
                (
                    "Guide des cotisations et obligations membres (FR)",
                    "Guide pratique pour les membres sur les cotisations et les droits d'accès",
                    "members_only",
                    "fr",
                    [
                        "La cotisation annuelle 2026 est fixée à 150 EUR pour les membres ordinaires. "
                        "Elle peut être réglée par virement bancaire ou en deux versements validés par le trésorier.",
                        "Un membre ordinaire dispose d'un accès en lecture à son profil, à ses cotisations, "
                        "aux annonces, aux documents publics de l'association et aux événements visibles.",
                        "Le chatbot peut rappeler au membre ses propres informations autorisées, mais ne peut "
                        "jamais divulguer les cotisations, sanctions ou données privées d'un autre adhérent.",
                    ],
                ),
                (
                    "Office Operations Handbook (EN)",
                    "Role summary for the office and committee members",
                    "tenant_public",
                    "en",
                    [
                        "The secretary general maintains statutes, protocols, and official announcements. "
                        "The treasurer manages contribution records and payment reconciliation.",
                        "The auditor has read-only finance oversight. The censor manages disciplinary cases "
                        "within explicit privacy limits. The sports manager maintains sports events and schedules.",
                        "Every privileged action remains enforced by the backend and recorded in the audit trail.",
                    ],
                ),
                (
                    "Leitfaden Sportbetrieb und Veranstaltungen (DE)",
                    "Sportkalender, Trainingsprinzipien und Veranstaltungsorganisation",
                    "tenant_public",
                    "de",
                    [
                        "Der Sportverantwortliche pflegt Trainings, Turniere und Spieltage im System. "
                        "Allgemeine Veranstaltungshinweise koennen fuer alle Mitglieder sichtbar veroeffentlicht werden.",
                        "Sportbezogene Regeln, Teilnahmebedingungen und Ansprechpersonen muessen klar "
                        "kommuniziert und fuer Mitglieder leicht auffindbar sein.",
                    ],
                ),
                (
                    "Proces-verbal Bureau T1 2026 (FR)",
                    "Synthèse interne du bureau pour le premier trimestre 2026",
                    "role_restricted",
                    "fr",
                    [
                        "Le bureau réuni en janvier 2026 a validé le calendrier sportif du premier semestre "
                        "et la publication d'un rappel général de cotisation aux membres en retard.",
                        "Le trésorier a présenté un taux de recouvrement de 72 pour cent sur les cotisations attendues. "
                        "Le secrétaire général a confirmé la mise à jour des documents de gouvernance.",
                    ],
                ),
            ]
            for title, desc, access_scope, language, chunks_text in doc_defs:
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
                    language=language,
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
                        language=language,
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
            bylaws_doc = docs_by_title.get("Statuts Combis Sport Verein (FR)")

            # ── Policies ───────────────────────────────────────────────────
            policy_defs = [
                (
                    "Politique de cotisation annuelle",
                    "financial",
                    "La cotisation annuelle est exigible au plus tard le 31 janvier. Les retards "
                    "importants peuvent déclencher un rappel formel et une restriction temporaire "
                    "des droits de vote jusqu'à régularisation.",
                    bylaws_doc.id if bylaws_doc else None,
                ),
                (
                    "Politique de participation aux assemblées",
                    "governance",
                    "Les membres sont encouragés à participer régulièrement aux assemblées et aux "
                    "réunions importantes. Des absences répétées non justifiées peuvent entraîner "
                    "un avertissement écrit.",
                    None,
                ),
                (
                    "Code de conduite associatif",
                    "conduct",
                    "Tout membre doit respecter les autres adhérents, les responsables et les invités "
                    "de l'association. Les comportements injurieux, discriminatoires ou violents peuvent "
                    "entraîner des sanctions allant de l'avertissement à l'exclusion.",
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
            if existing_contrib.scalars().first() is None:
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
                    DisciplinaryRecord.title == "Avertissement - absence à l'assemblée générale",
                )
            )
            if existing_disc.scalars().first() is None and bob_profile is not None:
                # Find attendance policy for linking
                pol_result = await db.execute(
                    select(PolicyRecord).where(
                        PolicyRecord.tenant_id == tenant.id,
                        PolicyRecord.title == "Politique de participation aux assemblées",
                    )
                )
                attendance_policy = pol_result.scalar_one_or_none()

                disc = DisciplinaryRecord(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    membership_profile_id=bob_profile.id,
                    policy_record_id=attendance_policy.id if attendance_policy else None,
                    title="Avertissement - absence à l'assemblée générale",
                    description="Boris Schneider a manqué l'assemblée générale du 1 mars 2026 "
                    "sans information préalable. Un avertissement écrit a été enregistré "
                    "conformément à la politique de participation.",
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
                (
                    "Football Training Session",
                    "Weekly sports training session for registered players and staff.",
                    NOW + timedelta(days=21),
                    NOW + timedelta(days=21, hours=2),
                    "Sports Field, Pitch 1",
                    "members_only",
                    "published",
                    {"workspace": "sports", "sport_type": "training"},
                ),
            ]
            for event_def in event_defs:
                if len(event_def) == 7:
                    title, desc, start, end, location, visibility, status = event_def
                    metadata = {}
                else:
                    title, desc, start, end, location, visibility, status, metadata = event_def
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
                    metadata_json=json.dumps(metadata, ensure_ascii=False),
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
