<template>
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
import type { BottomNavItem } from '@/components/ui/AppBottomNavigation.vue'

const route = useRoute()
const tenantStore = useTenantStore()
const localeStore = useLocaleStore()
const { moduleNavigation, appHomeLabel } = useRoleNavigation()

function isActive(destination: string) {
  return route.path === destination || (destination !== '/dashboard' && route.path.startsWith(`${destination}/`))
}

const bottomNavigation = computed<BottomNavItem[]>(() => {
  const workspace = moduleNavigation.value.find(
    (item) => !['/dashboard', '/members/profile', '/account/security', '/chat'].includes(item.to),
  )

  return [
    { id: '/dashboard', label: localeStore.t('nav.home'), icon: 'bi-house-door', active: isActive('/dashboard') },
    { id: '/members/profile', label: localeStore.t('nav.profile'), icon: 'bi-person', active: isActive('/members/profile') },
    { id: '/account/security', label: localeStore.t('nav.security'), icon: 'bi-shield-check', active: isActive('/account/security') },
    {
      id: '/chat',
      label: localeStore.t('nav.chat'),
      icon: 'bi-chat-dots',
      active: isActive('/chat'),
    },
    {
      id: workspace?.to || '/events',
      label: localeStore.t('nav.more'),
      icon: 'bi-three-dots',
      active: isActive(workspace?.to || '/events'),
    },
  ]
})
</script>
