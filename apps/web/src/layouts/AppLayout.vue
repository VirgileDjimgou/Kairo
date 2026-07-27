<template>
  <AppShell
    :eyebrow="appHomeLabel"
    :title="tenantStore.currentTenantName"
    icon="bi-grid-1x2"
    :navigation="appNavigation"
    :module-items="moduleNavigation"
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
import type { BottomNavItem } from '@/components/ui/AppBottomNavigation.vue'

const route = useRoute()
const tenantStore = useTenantStore()
const localeStore = useLocaleStore()
const { appNavigation, moduleNavigation, appHomeLabel } = useRoleNavigation()

function isActive(destination: string) {
  return route.path === destination || (destination !== '/dashboard' && route.path.startsWith(`${destination}/`))
}

const bottomNavigation = computed<BottomNavItem[]>(() => {
  const chatEnabled = tenantStore.isModuleEnabled('chat')
  const workspace = moduleNavigation.value.find(
    (item) => !['/dashboard', '/members/profile', '/account/security', '/chat'].includes(item.to),
  )

  return [
    { id: '/dashboard', label: localeStore.t('nav.home'), icon: 'bi-house-door', active: isActive('/dashboard') },
    { id: '/members/profile', label: localeStore.t('nav.profile'), icon: 'bi-person', active: isActive('/members/profile') },
    { id: '/account/security', label: localeStore.t('nav.security'), icon: 'bi-shield-check', active: isActive('/account/security') },
    {
      id: chatEnabled ? '/chat' : (workspace?.to || '/events'),
      label: chatEnabled ? localeStore.t('nav.chat') : localeStore.t('nav.more'),
      icon: chatEnabled ? 'bi-chat-dots' : 'bi-grid-3x3-gap',
      active: isActive(chatEnabled ? '/chat' : (workspace?.to || '/events')),
    },
    {
      id: chatEnabled ? (workspace?.to || '/events') : '/events',
      label: chatEnabled ? localeStore.t('nav.more') : localeStore.t('nav.events'),
      icon: 'bi-three-dots',
      active: isActive(chatEnabled ? (workspace?.to || '/events') : '/events'),
    },
  ]
})
</script>
