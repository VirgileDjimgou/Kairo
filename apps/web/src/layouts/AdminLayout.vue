<template>
  <AppShell
    :eyebrow="consoleSubtitle"
    :title="consoleTitle"
    icon="bi-shield-lock"
    :navigation="adminNavigation"
    :bottom-navigation="bottomNavigation"
    sidebar-class="admin-sidebar"
  >
    <RouterView v-slot="{ Component }">
      <Transition name="app-route" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { useRoleNavigation } from "@/composables/useRoleNavigation";
import { useTenantStore } from "@/stores/tenant.store";
import { useLocaleStore } from "@/stores/locale.store";
import AppShell from '@/components/ui/AppShell.vue'
import type { BottomNavItem } from '@/components/ui/MobileBottomNavigation.vue'

const route = useRoute()
const tenantStore = useTenantStore()
const localeStore = useLocaleStore()
const { adminNavigation, isPrincipalAdmin } = useRoleNavigation()

const consoleTitle = computed(() =>
  isPrincipalAdmin.value ? localeStore.t('layout.principalAdminConsole') : localeStore.t('layout.adminConsole'),
)
const consoleSubtitle = computed(() =>
  isPrincipalAdmin.value ? localeStore.t('layout.principalAdminSubtitle') : localeStore.t('layout.adminSubtitle'),
)

function isActive(destination: string) {
  return destination === '/admin'
    ? route.path === destination
    : route.path === destination || route.path.startsWith(`${destination}/`)
}

const bottomNavigation = computed<BottomNavItem[]>(() => [
  { id: '/admin', label: localeStore.t('nav.home'), icon: 'bi-house-door', active: isActive('/admin') },
  { id: '/members/profile', label: localeStore.t('nav.profile'), icon: 'bi-person', active: isActive('/members/profile') },
  { id: '/account/security', label: localeStore.t('nav.security'), icon: 'bi-shield-check', active: isActive('/account/security') },
  {
    id: tenantStore.isModuleEnabled('chat') ? '/chat' : '/admin/documents',
    label: tenantStore.isModuleEnabled('chat') ? localeStore.t('nav.chat') : localeStore.t('nav.workspace'),
    icon: tenantStore.isModuleEnabled('chat') ? 'bi-chat-dots' : 'bi-file-earmark-text',
    active: isActive(tenantStore.isModuleEnabled('chat') ? '/chat' : '/admin/documents'),
  },
  { id: '/admin/settings', label: localeStore.t('nav.workspace'), icon: 'bi-gear', active: isActive('/admin/settings') },
])
</script>
