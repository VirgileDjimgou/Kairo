<template>
  <AppShell
    :eyebrow="consoleSubtitle"
    :title="consoleTitle"
    icon="bi-shield-lock"
    :module-items="adminModuleNavigation"
    :bottom-navigation="bottomNavigation"
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
import type { BottomNavItem } from '@/components/ui/AppBottomNavigation.vue'

const route = useRoute()
const tenantStore = useTenantStore()
const localeStore = useLocaleStore()
const { adminModuleNavigation, isPrincipalAdmin } = useRoleNavigation()

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
    label: tenantStore.isModuleEnabled('chat') ? localeStore.t('nav.chat') : localeStore.t('nav.documents'),
    icon: tenantStore.isModuleEnabled('chat') ? 'bi-chat-dots' : 'bi-file-earmark-text',
    active: isActive(tenantStore.isModuleEnabled('chat') ? '/chat' : '/admin/documents'),
  },
  { id: '/admin/settings', label: localeStore.t('nav.more'), icon: 'bi-three-dots', active: isActive('/admin/settings') },
])
</script>
