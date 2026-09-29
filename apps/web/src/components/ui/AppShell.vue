<template>
  <div class="app-shell om-min-viewport-height" :style="brandStyle">
    <a class="skip-link" href="#kairo-main-content">{{ localeStore.t('layout.skipToContent') }}</a>
    <AppTopBar
      :eyebrow="eyebrow"
      :title="tenantStore.currentTenantName || title"
      :icon="icon"
      :user-name="authStore.user?.display_name || ''"
      :user-email="authStore.user?.email || ''"
      :account-label="localeStore.t('layout.account')"
      :account-security-label="localeStore.t('layout.accountSecurity')"
      :signed-in-as-label="localeStore.t('layout.signedInAs')"
      :sign-out-label="localeStore.t('layout.signOut')"
      @logout="handleLogout"
    />

    <RoleTopNavigation
      :items="moduleItems"
      :label="localeStore.t('layout.mobileNavigation')"
    />

    <main id="kairo-main-content" class="app-shell__content" tabindex="-1">
      <div class="app-shell__content-inner">
        <slot />
      </div>
    </main>

    <AppBottomNavigation
      v-if="bottomNavigation.length"
      :items="bottomNavigation"
      :aria-label="localeStore.t('layout.mobileNavigation')"
      @navigate="navigate"
    />

    <GlobalSearchOverlay :open="searchOpen" @close="searchOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import type { NavItem } from '@/composables/useRoleNavigation'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import AppBottomNavigation from '@/components/ui/AppBottomNavigation.vue'
import RoleTopNavigation from '@/components/ui/RoleTopNavigation.vue'
import GlobalSearchOverlay from '@/components/search/GlobalSearchOverlay.vue'
import type { BottomNavItem } from '@/components/ui/AppBottomNavigation.vue'

defineProps<{
  eyebrow: string
  title: string
  icon: string
  moduleItems: NavItem[]
  bottomNavigation: BottomNavItem[]
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const localeStore = useLocaleStore()
const tenantStore = useTenantStore()

const brandStyle = computed(() => ({
  '--om-primary': tenantStore.currentTenant?.branding.primary_color || '#1E63B5',
}))

const searchOpen = ref(false)

function handleSearchHotkey(event: KeyboardEvent) {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    searchOpen.value = !searchOpen.value
  }
}

onMounted(() => window.addEventListener('keydown', handleSearchHotkey))
onUnmounted(() => window.removeEventListener('keydown', handleSearchHotkey))

function navigate(destination: string) {
  void router.push(destination)
}

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<style scoped>
.skip-link {
  position: absolute;
  left: -10000px;
  top: auto;
  width: 1px;
  height: 1px;
  overflow: hidden;
}

.skip-link:focus {
  position: fixed;
  left: 1rem;
  top: 1rem;
  width: auto;
  height: auto;
  padding: 0.5rem 0.75rem;
  background: var(--om-primary);
  color: #ffffff;
  border-radius: var(--om-radius-sm);
  z-index: 1080;
}

.app-shell {
  width: 100%;
  max-width: 100%;
  min-height: 100dvh;
  background: var(--om-neutral-50);
  display: flex;
  flex-direction: column;
}

.app-shell__content {
  flex: 1 1 auto;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding-bottom: calc(var(--om-bottomnav-height) + env(safe-area-inset-bottom, 0px) + 1rem);
}

.app-shell__content-inner {
  width: 100%;
  max-width: var(--om-content-max-width);
  margin: 0 auto;
  padding: 0 max(1rem, env(safe-area-inset-left, 0px)) 0 max(1rem, env(safe-area-inset-right, 0px));
  min-width: 0;
}
</style>
