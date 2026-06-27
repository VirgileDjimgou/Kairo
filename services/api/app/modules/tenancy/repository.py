from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tenancy.models import Role, Tenant, TenantUser, user_roles


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

    async def create_tenant(
        self,
        slug: str,
        name: str,
        tenant_type: str = "association",
        default_language: str = "en",
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

    async def assign_role_to_user(
        self, tenant_id: UUID, user_id: UUID, role_id: UUID
    ) -> None:
        """Assign a role to a tenant user. Idempotent — safe to call twice."""
        tenant_user = await self.get_tenant_user(tenant_id, user_id)
        if not tenant_user:
            raise ValueError(
                f"User {user_id} is not a member of tenant {tenant_id}"
            )
        # Insert into user_roles (ignore conflict)
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        stmt = pg_insert(user_roles).values(
            tenant_user_id=tenant_user.id, role_id=role_id
        ).on_conflict_do_nothing()
        await self._db.execute(stmt)
