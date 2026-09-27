from uuid import UUID

from fastapi import HTTPException, status

from app.modules.audit.schemas import AuditEventResponse
from app.modules.identity.base import IdentityServiceBase
from app.modules.identity.schemas import (
    ManagedTenantUserActionResponse,
    ManagedTenantUserResponse,
    ManagedTenantUserRolesUpdateRequest,
    ManagedTenantUserRolesUpdateResponse,
)


class AdministrationMixin(IdentityServiceBase):
    async def list_managed_users(
        self,
        *,
        tenant_id: UUID,
        requesting_user_id: UUID,
    ) -> list[ManagedTenantUserResponse]:
        await self._require_admin(tenant_id, requesting_user_id)
        rows = await self._tenancy_repo.list_tenant_user_details(tenant_id)
        user_ids = [user.id for _, user in rows]
        session_counts = await self._session_repo.count_active_for_users_by_tenant(
            tenant_id=tenant_id,
            user_ids=user_ids,
        )
        latest_events = await self._latest_identity_events_for_users(
            tenant_id=tenant_id,
            user_ids=user_ids,
        )
        result: list[ManagedTenantUserResponse] = []
        for membership, user in rows:
            roles = await self._tenancy_repo.get_user_role_codes(tenant_id, user.id)
            latest_event = latest_events.get(user.id)
            result.append(
                ManagedTenantUserResponse(
                    user_id=user.id,
                    email=user.email,
                    display_name=user.display_name,
                    profile_type=membership.profile_type,
                    membership_status=membership.membership_status,
                    user_status=user.status,
                    roles=roles,
                    last_login_at=user.last_login_at,
                    active_session_count=session_counts.get(user.id, 0),
                    last_security_event_action=(
                        latest_event.action if latest_event is not None else None
                    ),
                    last_security_event_at=(
                        latest_event.created_at if latest_event is not None else None
                    ),
                )
            )
        return result
    async def suspend_tenant_user(
        self,
        *,
        tenant_id: UUID,
        target_user_id: UUID,
        requesting_user_id: UUID,
        actor_user_id: UUID | None = None,
    ) -> ManagedTenantUserActionResponse:
        await self._require_admin(tenant_id, requesting_user_id)
        if target_user_id == requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use a different administrator to suspend this account.",
            )
        membership = await self._tenancy_repo.get_tenant_user(tenant_id, target_user_id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Managed user not found",
            )
        previous_status = membership.membership_status
        if previous_status == "suspended":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This tenant user is already suspended",
            )
        updated_membership = await self._tenancy_repo.update_membership_status(
            tenant_id,
            target_user_id,
            "suspended",
        )
        revoked_sessions = await self._session_repo.revoke_all_for_user_and_tenant(
            user_id=target_user_id,
            tenant_id=tenant_id,
            revoked_reason="admin_suspended_membership",
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="tenant_user_suspended",
            entity_type="tenant_user",
            entity_id=membership.id,
            module_key="identity",
            details={
                "user_id": target_user_id,
                "previous_status": previous_status,
                "new_status": "suspended",
                "revoked_session_count": len(revoked_sessions),
            },
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id or requesting_user_id,
            revoked_sessions=revoked_sessions,
            reason="admin_suspended_membership",
        )
        await self._db.commit()
        return ManagedTenantUserActionResponse(
            message="The tenant user has been suspended and active tenant sessions were revoked.",
            membership_status=(
                updated_membership.membership_status
                if updated_membership is not None
                else "suspended"
            ),
            revoked_session_count=len(revoked_sessions),
        )
    async def reactivate_tenant_user(
        self,
        *,
        tenant_id: UUID,
        target_user_id: UUID,
        requesting_user_id: UUID,
        actor_user_id: UUID | None = None,
    ) -> ManagedTenantUserActionResponse:
        await self._require_admin(tenant_id, requesting_user_id)
        membership = await self._tenancy_repo.get_tenant_user(tenant_id, target_user_id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Managed user not found",
            )
        previous_status = membership.membership_status
        if previous_status == "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This tenant user is already active",
            )
        updated_membership = await self._tenancy_repo.update_membership_status(
            tenant_id,
            target_user_id,
            "active",
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="tenant_user_reactivated",
            entity_type="tenant_user",
            entity_id=membership.id,
            module_key="identity",
            details={
                "user_id": target_user_id,
                "previous_status": previous_status,
                "new_status": "active",
            },
        )
        await self._db.commit()
        return ManagedTenantUserActionResponse(
            message="The tenant user has been reactivated.",
            membership_status=(
                updated_membership.membership_status
                if updated_membership is not None
                else "active"
            ),
            revoked_session_count=0,
        )
    async def revoke_tenant_user_sessions(
        self,
        *,
        tenant_id: UUID,
        target_user_id: UUID,
        requesting_user_id: UUID,
        actor_user_id: UUID | None = None,
    ) -> ManagedTenantUserActionResponse:
        await self._require_admin(tenant_id, requesting_user_id)
        if target_user_id == requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use account security to revoke your own sessions.",
            )
        membership = await self._tenancy_repo.get_tenant_user(tenant_id, target_user_id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Managed user not found",
            )
        revoked_sessions = await self._session_repo.revoke_all_for_user_and_tenant(
            user_id=target_user_id,
            tenant_id=tenant_id,
            revoked_reason="admin_forced_tenant_revocation",
        )
        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            action="tenant_user_sessions_revoked",
            entity_type="tenant_user",
            entity_id=membership.id,
            module_key="identity",
            details={
                "user_id": target_user_id,
                "revoked_session_count": len(revoked_sessions),
            },
        )
        await self._record_session_revocation_events(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id or requesting_user_id,
            revoked_sessions=revoked_sessions,
            reason="admin_forced_tenant_revocation",
        )
        await self._db.commit()
        return ManagedTenantUserActionResponse(
            message="Active tenant sessions were revoked for the managed user.",
            membership_status=membership.membership_status,
            revoked_session_count=len(revoked_sessions),
        )
    async def update_tenant_user_roles(
        self,
        *,
        tenant_id: UUID,
        target_user_id: UUID,
        requesting_user_id: UUID,
        request: ManagedTenantUserRolesUpdateRequest,
        actor_user_id: UUID | None = None,
    ) -> ManagedTenantUserRolesUpdateResponse:
        await self._require_admin(tenant_id, requesting_user_id)
        if target_user_id == requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use another administrator account to modify your own roles.",
            )

        await self._tenancy_repo.ensure_canonical_role_catalog(tenant_id)
        membership = await self._tenancy_repo.get_tenant_user(tenant_id, target_user_id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Managed user not found in this organization",
            )

        normalized_role_codes = list(dict.fromkeys(request.role_codes))
        resolved_roles = []
        for role_code in normalized_role_codes:
            role = await self._tenancy_repo.get_role_by_code(tenant_id, role_code)
            if role is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role '{role_code}' does not exist in this organization",
                )
            resolved_roles.append(role)

        previous_roles, updated_roles = await self._tenancy_repo.replace_user_roles(
            tenant_id=tenant_id,
            user_id=target_user_id,
            role_ids=[role.id for role in resolved_roles],
        )
        previous_role_codes = sorted(role.code for role in previous_roles)
        updated_role_codes = sorted(role.code for role in updated_roles)

        await self._audit.record_event(
            tenant_id=tenant_id,
            actor_user_id=requesting_user_id if actor_user_id is None else actor_user_id,
            action="roles_updated",
            entity_type="tenant_user",
            entity_id=membership.id,
            module_key="identity",
            details={
                "target_user_id": target_user_id,
                "previous_role_codes": previous_role_codes,
                "role_codes": updated_role_codes,
                "added_role_codes": sorted(set(updated_role_codes) - set(previous_role_codes)),
                "removed_role_codes": sorted(set(previous_role_codes) - set(updated_role_codes)),
            },
        )
        await self._db.commit()

        return ManagedTenantUserRolesUpdateResponse(
            message="Tenant roles updated successfully.",
            role_codes=updated_role_codes,
        )

    async def _latest_identity_events_for_users(
        self,
        *,
        tenant_id: UUID,
        user_ids: list[UUID],
    ) -> dict[UUID, AuditEventResponse]:
        if not user_ids:
            return {}
        user_id_set = set(user_ids)
        events = await self._audit.list_events(
            tenant_id,
            limit=max(100, len(user_ids) * 6),
            offset=0,
            module_key="identity",
        )
        latest: dict[UUID, AuditEventResponse] = {}
        for event in events:
            target_user_id = self._resolve_identity_event_user_id(event)
            if target_user_id is None or target_user_id not in user_id_set:
                continue
            if target_user_id in latest:
                continue
            latest[target_user_id] = event
        return latest
    def _resolve_identity_event_user_id(
        self,
        event: AuditEventResponse,
    ) -> UUID | None:
        details = event.details if isinstance(event.details, dict) else {}
        if event.actor_user_id is not None:
            return event.actor_user_id
        details_user_id = details.get("user_id") or details.get("session_user_id")
        if details_user_id:
            try:
                return UUID(str(details_user_id))
            except ValueError:
                return None
        if event.entity_type in {"mfa", "password_reset"} and event.entity_id:
            try:
                return UUID(str(event.entity_id))
            except ValueError:
                return None
        return None
