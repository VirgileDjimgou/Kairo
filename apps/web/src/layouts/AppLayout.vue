<template>
  <DemoSessionBanner />
  <AppShell
    :eyebrow="appHomeLabel"
    :title="tenantStore.currentTenantName"
    icon="bi-grid-1x2"
    :module-items="moduleNavigation"
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
import DemoSessionBanner from '@/components/DemoSessionBanner.vue'
import type { BottomNavItem } from '@/components/ui/AppBottomNavigation.vue'

const route = useRoute()
const tenantStore = useTenantStore()
const localeStore = useLocaleStore()
const { moduleNavigation, appHomeLabel, isMember } = useRoleNavigation()

function isActive(destination: string) {
  return route.path === destination || (destination !== '/dashboard' && route.path.startsWith(`${destination}/`))
}

const bottomNavigation = computed<BottomNavItem[]>(() => {
  const home = { id: '/dashboard', label: localeStore.t('nav.home'), icon: 'bi-house-door', active: isActive('/dashboard') }
  const notifications = { id: '/notifications', label: localeStore.t('nav.notifications'), icon: 'bi-bell', active: isActive('/notifications') }
  const more = { id: '/more', label: localeStore.t('nav.more'), icon: 'bi-three-dots', active: isActive('/more') }

  if (isMember.value) {
    return [
      home,
      { id: '/chat', label: localeStore.t('nav.chat'), icon: 'bi-chat-dots', active: isActive('/chat') },
      notifications,
      more,
    ]
  }

  return [
    home,
    { id: '/tasks', label: localeStore.t('nav.tasks'), icon: 'bi-list-check', active: isActive('/tasks') },
    { id: '/search', label: localeStore.t('nav.search'), icon: 'bi-search', active: isActive('/search') },
    notifications,
    more,
  ]
})
</script>
