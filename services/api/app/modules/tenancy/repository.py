from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.models import User
from app.modules.tenancy.models import Role, Tenant, TenantUser, user_roles
from app.modules.tenancy.role_catalog import canonical_role_definitions


class TenancyRepository:
    """
    Data access for tenants, memberships, and roles.

    All query methods that return tenant-specific data require tenant_id
    to enforce isolation. Never query across tenants.
    """

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── Tenants ────────────────────────────────────────────────────────────────

    async def get_tenant_by_id(self, tenant_id: UUID) -> Tenant | None:
        result = await self._db.execute(
            select(Tenant).where(Tenant.id == tenant_id, Tenant.status == "active")
        )
        return result.scalar_one_or_none()

    async def get_tenant_by_slug(self, slug: str) -> Tenant | None:
        result = await self._db.execute(
            select(Tenant).where(
                Tenant.slug == slug.lower().strip(),
                Tenant.status == "active",
            )
        )
        return result.scalar_one_or_none()

    async def update_tenant(
        self, tenant_id: UUID, *, name: str | None = None,
        default_language: str | None = None,
        branding_json: str | None = None,
        settings_json: str | None = None,
    ) -> Tenant | None:
        tenant = await self.get_tenant_by_id(tenant_id)
        if not tenant:
            return None
        if name is not None:
            tenant.name = name
        if default_language is not None:
            tenant.default_language = default_language
        if branding_json is not None:
            tenant.branding_json = branding_json
        if settings_json is not None:
            tenant.settings_json = settings_json
        await self._db.flush()
        await self._db.refresh(tenant)
        return tenant

    async def create_tenant(
        self,
        slug: str,
        name: str,
        tenant_type: str = "association",
        default_language: str = "fr",
    ) -> Tenant:
        tenant = Tenant(
            slug=slug.lower().strip(),
            name=name,
            type=tenant_type,
            default_language=default_language,
        )
        self._db.add(tenant)
        await self._db.flush()
        await self._db.refresh(tenant)
        return tenant

    # ── Memberships ────────────────────────────────────────────────────────────

    async def get_tenant_user(
        self, tenant_id: UUID, user_id: UUID
    ) -> TenantUser | None:
        """
        Tenant isolation check: verify user is an active member of tenant.
        Called before any tenant-scoped operation.
        """
        result = await self._db.execute(
            select(TenantUser).where(
                TenantUser.tenant_id == tenant_id,
                TenantUser.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_active_memberships(self, user_id: UUID) -> list[TenantUser]:
        """Return all active tenant memberships for a user (for tenant selection on login)."""
        result = await self._db.execute(
            select(TenantUser).where(
                TenantUser.user_id == user_id,
                TenantUser.membership_status == "active",
            )
        )
        return list(result.scalars().all())

    async def get_tenant_members(
        self, tenant_id: UUID, status: str | None = "active"
    ) -> list[TenantUser]:
        """
        List all members of a tenant.
        Always scoped by tenant_id — never returns cross-tenant data.
        """
        query = select(TenantUser).where(TenantUser.tenant_id == tenant_id)
        if status:
            query = query.where(TenantUser.membership_status == status)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def list_tenant_user_details(
        self, tenant_id: UUID
    ) -> list[tuple[TenantUser, User]]:
        result = await self._db.execute(
            select(TenantUser, User)
            .join(User, User.id == TenantUser.user_id)
            .where(TenantUser.tenant_id == tenant_id)
            .order_by(User.display_name.asc(), User.email.asc())
        )
        return list(result.all())

    async def create_tenant_user(
        self,
        tenant_id: UUID,
        user_id: UUID,
        profile_type: str = "member",
        membership_status: str = "active",
    ) -> TenantUser:
        tu = TenantUser(
            tenant_id=tenant_id,
            user_id=user_id,
            profile_type=profile_type,
            membership_status=membership_status,
        )
        self._db.add(tu)
        await self._db.flush()
        await self._db.refresh(tu)
        return tu

    async def update_membership_status(
        self,
        tenant_id: UUID,
        user_id: UUID,
        membership_status: str,
    ) -> TenantUser | None:
        membership = await self.get_tenant_user(tenant_id, user_id)
        if membership is None:
            return None
        membership.membership_status = membership_status
        membership.updated_at = datetime.now(timezone.utc)
        await self._db.flush()
        await self._db.refresh(membership)
        return membership

    # ── Roles ──────────────────────────────────────────────────────────────────

    async def get_roles_for_tenant(self, tenant_id: UUID) -> list[Role]:
        result = await self._db.execute(
            select(Role).where(Role.tenant_id == tenant_id)
        )
        return list(result.scalars().all())

    async def get_role_by_code(self, tenant_id: UUID, code: str) -> Role | None:
        result = await self._db.execute(
            select(Role).where(Role.tenant_id == tenant_id, Role.code == code)
        )
        return result.scalar_one_or_none()

    async def get_user_roles(self, tenant_id: UUID, user_id: UUID) -> list[Role]:
        """
        Return all roles assigned to a user within a specific tenant.
        Used during login to populate the JWT roles claim.
        """
        # Resolve tenant_user_id first
        tenant_user = await self.get_tenant_user(tenant_id, user_id)
        if not tenant_user:
            return []

        result = await self._db.execute(
            select(Role)
            .join(user_roles, Role.id == user_roles.c.role_id)
            .where(
                user_roles.c.tenant_user_id == tenant_user.id,
                Role.tenant_id == tenant_id,
            )
            .order_by(Role.code.asc())
        )
        return list(result.scalars().all())

    async def get_user_role_codes(self, tenant_id: UUID, user_id: UUID) -> list[str]:
        """Return only role codes — used to populate the JWT claim."""
        roles = await self.get_user_roles(tenant_id, user_id)
        return [r.code for r in roles]

    async def create_role(
        self,
        tenant_id: UUID,
        code: str,
        name: str,
        description: str | None = None,
        is_system_role: bool = False,
    ) -> Role:
        role = Role(
            tenant_id=tenant_id,
            code=code,
            name=name,
            description=description,
            is_system_role=is_system_role,
        )
        self._db.add(role)
        await self._db.flush()
        await self._db.refresh(role)
        return role

    async def ensure_canonical_role_catalog(self, tenant_id: UUID) -> list[Role]:
        existing_roles = {
            role.code: role for role in await self.get_roles_for_tenant(tenant_id)
        }
        for definition in canonical_role_definitions():
            role = existing_roles.get(definition.code)
            if role is None:
                role = Role(
                    tenant_id=tenant_id,
                    code=definition.code,
                    name=definition.name,
                    description=definition.description,
                    is_system_role=definition.is_system_role,
                )
                self._db.add(role)
                await self._db.flush()
                existing_roles[definition.code] = role
                continue

            role.name = definition.name
            role.description = definition.description
            role.is_system_role = definition.is_system_role

        await self._db.flush()
        return await self.get_roles_for_tenant(tenant_id)

    async def assign_role_to_user(
        self, tenant_id: UUID, user_id: UUID, role_id: UUID
    ) -> None:
        """Assign a role to a tenant user. Idempotent — safe to call twice."""
        tenant_user = await self.get_tenant_user(tenant_id, user_id)
        if not tenant_user:
            raise ValueError(
                f"User {user_id} is not a member of tenant {tenant_id}"
            )
        dialect_name = self._db.bind.dialect.name if self._db.bind else ""
        if dialect_name == "sqlite":
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            stmt = sqlite_insert(user_roles).values(
                tenant_user_id=tenant_user.id, role_id=role_id
            ).prefix_with("OR IGNORE")
        else:
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            stmt = pg_insert(user_roles).values(
                tenant_user_id=tenant_user.id, role_id=role_id
            ).on_conflict_do_nothing()
        await self._db.execute(stmt)

    async def replace_user_roles(
        self,
        tenant_id: UUID,
        user_id: UUID,
        role_ids: list[UUID],
    ) -> tuple[list[Role], list[Role]]:
        tenant_user = await self.get_tenant_user(tenant_id, user_id)
        if not tenant_user:
            raise ValueError(
                f"User {user_id} is not a member of tenant {tenant_id}"
            )

        current_roles = await self.get_user_roles(tenant_id, user_id)
        current_role_ids = {role.id for role in current_roles}
        target_role_ids = list(dict.fromkeys(role_ids))
        target_role_id_set = set(target_role_ids)

        removed_role_ids = current_role_ids - target_role_id_set
        if removed_role_ids:
            await self._db.execute(
                delete(user_roles).where(
                    user_roles.c.tenant_user_id == tenant_user.id,
                    user_roles.c.role_id.in_(removed_role_ids),
                )
            )

        for role_id in target_role_ids:
            if role_id not in current_role_ids:
                await self.assign_role_to_user(tenant_id, user_id, role_id)

        await self._db.flush()
        updated_roles = await self.get_user_roles(tenant_id, user_id)
        return current_roles, updated_roles
