import json
from uuid import UUID

from fastapi import HTTPException, status

from app.core.capabilities import (
    capabilities_for_roles,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
)
from app.modules.identity.base import (
    SUPPORTED_INTERFACE_LANGUAGES,
    IdentityServiceBase,
)
from app.modules.identity.schemas import (
    LanguagePreferenceResponse,
    SwitchTenantRequest,
    SwitchTenantResponse,
    TenantMembershipResponse,
    UpdateLanguagePreferenceRequest,
)
from app.modules.tenancy.module_toggles import parse_module_toggles
from app.modules.tenancy.schemas import BrandingConfig, ModuleToggles


class TenancyMixin(IdentityServiceBase):
    async def get_user_memberships(
        self, user_id: UUID
    ) -> list[TenantMembershipResponse]:
        memberships = await self._tenancy_repo.get_user_active_memberships(user_id)
        result: list[TenantMembershipResponse] = []
        for tu in memberships:
            tenant = await self._tenancy_repo.get_tenant_by_id(tu.tenant_id)
            if not tenant:
                continue
            roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user_id)

            branding_raw: dict[str, object] = {}
            if isinstance(tenant.branding_json, str) and tenant.branding_json.strip():
                try:
                    branding_raw = json.loads(tenant.branding_json)
                except json.JSONDecodeError:
                    branding_raw = {}

            settings_raw: dict[str, object] = {}
            if isinstance(tenant.settings_json, str) and tenant.settings_json.strip():
                try:
                    settings_raw = json.loads(tenant.settings_json)
                except json.JSONDecodeError:
                    settings_raw = {}

            module_toggles = parse_module_toggles(settings_raw)
            branding = BrandingConfig(**branding_raw) if branding_raw else BrandingConfig()  # type: ignore[arg-type]

            result.append(
                TenantMembershipResponse(
                    tenant_id=tenant.id,
                    slug=tenant.slug,
                    name=tenant.name,
                    default_language=tenant.default_language,
                    roles=roles,
                    capabilities=list(capabilities_for_roles(roles)),
                    branding=branding,
                    modules=ModuleToggles(**module_toggles),
                    profile_type=tu.profile_type,
                )
            )
        return result
    async def update_language_preference(
        self,
        *,
        user_id: UUID,
        request: UpdateLanguagePreferenceRequest,
    ) -> LanguagePreferenceResponse:
        preferred_language = request.preferred_language.strip().lower()
        if preferred_language not in SUPPORTED_INTERFACE_LANGUAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Supported languages are fr, en, and de",
            )
        await self._user_repo.update_preferred_language(user_id, preferred_language)
        await self._db.commit()
        return LanguagePreferenceResponse(preferred_language=preferred_language)
    async def switch_tenant(
        self,
        user_id: UUID,
        request: SwitchTenantRequest,
        *,
        session_id: UUID,
    ) -> SwitchTenantResponse:
        membership = await self._tenancy_repo.get_tenant_user(
            request.tenant_id, user_id
        )
        if not membership or membership.membership_status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not an active member of this organization",
            )

        tenant = await self._tenancy_repo.get_tenant_by_id(request.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        roles = await self._tenancy_repo.get_user_role_codes(tenant.id, user_id)
        await self._session_repo.touch(
            session_id,
            tenant_id=tenant.id,
            ip_address=self._request_ip,
            user_agent=self._request_user_agent,
        )
        token = create_access_token(
            user_id=user_id,
            tenant_id=tenant.id,
            roles=roles,
            session_id=session_id,
        )

        memberships = await self.get_user_memberships(user_id)
        await self._db.commit()

        return SwitchTenantResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            tenant_id=tenant.id,
            user_id=user_id,
            memberships=memberships,
        )
