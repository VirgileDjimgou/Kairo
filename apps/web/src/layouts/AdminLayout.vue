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
import { useLocaleStore } from "@/stores/locale.store";
import AppShell from '@/components/ui/AppShell.vue'
import type { BottomNavItem } from '@/components/ui/AppBottomNavigation.vue'

const route = useRoute()
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
  { id: '/tasks', label: localeStore.t('nav.tasks'), icon: 'bi-list-check', active: isActive('/tasks') },
  { id: '/search', label: localeStore.t('nav.search'), icon: 'bi-search', active: isActive('/search') },
  { id: '/notifications', label: localeStore.t('nav.notifications'), icon: 'bi-bell', active: isActive('/notifications') },
  { id: '/more', label: localeStore.t('nav.more'), icon: 'bi-three-dots', active: isActive('/more') },
])
</script>
