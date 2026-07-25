<template>
  <AppShell
    :eyebrow="appHomeLabel"
    :title="tenantStore.currentTenantName"
    icon="bi-grid-1x2"
    :navigation="appNavigation"
    :bottom-navigation="bottomNavigation"
    sidebar-class="sidebar"
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
const { appNavigation, appHomeLabel } = useRoleNavigation()

function isActive(destination: string) {
  return route.path === destination || (destination !== '/dashboard' && route.path.startsWith(`${destination}/`))
}

const bottomNavigation = computed<BottomNavItem[]>(() => {
  const workspace = appNavigation.value
    .flatMap((section) => section.items)
    .find((item) => !['/dashboard', '/members/profile', '/account/security', '/chat'].includes(item.to))

  const fifthDestination = workspace?.to || '/events'
  const fifthIcon = workspace?.icon || 'bi-grid-3x3-gap'
  const chatEnabled = tenantStore.isModuleEnabled('chat')

  return [
    { id: '/dashboard', label: localeStore.t('nav.home'), icon: 'bi-house-door', active: isActive('/dashboard') },
    { id: '/members/profile', label: localeStore.t('nav.profile'), icon: 'bi-person', active: isActive('/members/profile') },
    { id: '/account/security', label: localeStore.t('nav.security'), icon: 'bi-shield-check', active: isActive('/account/security') },
    {
      id: chatEnabled ? '/chat' : fifthDestination,
      label: chatEnabled ? localeStore.t('nav.chat') : localeStore.t('nav.workspace'),
      icon: chatEnabled ? 'bi-chat-dots' : fifthIcon,
      active: isActive(chatEnabled ? '/chat' : fifthDestination),
    },
    { id: fifthDestination, label: localeStore.t('nav.workspace'), icon: fifthIcon, active: isActive(fifthDestination) },
  ]
})
</script>
