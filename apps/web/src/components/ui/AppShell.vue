<template>
  <div class="app-shell om-min-viewport-height" :style="brandStyle">
    <aside :class="['app-shell__sidebar', sidebarClass]">
      <div class="app-shell__brand">
        <i class="bi" :class="icon" aria-hidden="true"></i>
        <span>{{ title }}</span>
      </div>

      <nav class="app-shell__sidebar-navigation">
        <section v-for="section in navigation" :key="section.label">
          <div class="app-shell__sidebar-label">{{ section.label }}</div>
          <RouterLink
            v-for="item in section.items"
            :key="item.to"
            :to="item.to"
            class="sidebar-link"
            :class="{ active: isActive(item.to) }"
            :aria-current="isActive(item.to) ? 'page' : undefined"
          >
            <i class="bi" :class="item.icon" aria-hidden="true"></i>
            <span>{{ item.label }}</span>
          </RouterLink>
        </section>
      </nav>

      <div class="app-shell__sidebar-account">
        <div class="app-shell__sidebar-user">
          <i class="bi bi-person-circle" aria-hidden="true"></i>
          <div>
            <strong>{{ authStore.user?.display_name }}</strong>
            <span>{{ authStore.user?.email }}</span>
          </div>
        </div>
        <button class="btn btn-outline-secondary w-100" @click="handleLogout">
          <i class="bi bi-box-arrow-right"></i>
          <span>{{ localeStore.t('layout.signOut') }}</span>
        </button>
      </div>
    </aside>

    <main class="app-shell__main">
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
        :sections="navigation"
        :label="localeStore.t('layout.mobileNavigation')"
      />

      <section class="app-shell__content">
        <slot />
      </section>
    </main>

    <MobileBottomNavigation
      v-if="bottomNavigation.length"
      :items="bottomNavigation"
      :aria-label="localeStore.t('layout.mobileNavigation')"
      class="app-shell__bottom-navigation"
      @navigate="navigate"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import type { NavSection } from '@/composables/useRoleNavigation'
import AppTopBar from '@/components/ui/AppTopBar.vue'
import MobileBottomNavigation from '@/components/ui/MobileBottomNavigation.vue'
import RoleTopNavigation from '@/components/ui/RoleTopNavigation.vue'
import type { BottomNavItem } from '@/components/ui/MobileBottomNavigation.vue'

const props = withDefaults(defineProps<{
  eyebrow: string
  title: string
  icon: string
  navigation: NavSection[]
  bottomNavigation: BottomNavItem[]
  sidebarClass?: string
}>(), {
  sidebarClass: '',
})

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const localeStore = useLocaleStore()
const tenantStore = useTenantStore()

const brandStyle = computed(() => ({
  '--om-primary': tenantStore.currentTenant?.branding.primary_color || '#1e63b5',
}))

function isActive(destination: string) {
  return route.path === destination || (destination !== '/dashboard' && destination !== '/admin' && route.path.startsWith(`${destination}/`))
}

function navigate(destination: string) {
  void router.push(destination)
}

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<style scoped>
.app-shell {
  width: 100%;
  max-width: 100%;
  background: var(--om-neutral-50);
}

.app-shell__sidebar {
  display: none;
  width: var(--om-sidebar-width);
  min-width: var(--om-sidebar-width);
  height: 100dvh;
  flex: 0 0 var(--om-sidebar-width);
  flex-direction: column;
  overflow-y: auto;
  padding: 1.25rem;
  background: var(--om-neutral-0);
  border-right: 1px solid var(--om-neutral-200);
}

.app-shell__brand {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  color: var(--om-neutral-900);
  font-weight: 750;
}

.app-shell__brand i {
  display: inline-grid;
  width: 2.25rem;
  height: 2.25rem;
  flex: 0 0 auto;
  place-items: center;
  border-radius: var(--om-radius-base);
  background: var(--om-primary-subtle);
  color: var(--om-primary);
}

.app-shell__brand span,
.app-shell__sidebar-user strong,
.app-shell__sidebar-user span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-shell__sidebar-navigation {
  display: grid;
  gap: 1.25rem;
}

.app-shell__sidebar-navigation section {
  display: grid;
  gap: 0.25rem;
}

.app-shell__sidebar-label {
  padding-inline: 0.75rem;
  color: var(--om-neutral-600);
  font-size: 0.6875rem;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.app-shell__sidebar-navigation .sidebar-link {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.625rem;
}

.app-shell__sidebar-navigation .sidebar-link span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-shell__sidebar-account {
  display: grid;
  gap: 0.75rem;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--om-neutral-200);
}

.app-shell__sidebar-user {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.625rem;
}

.app-shell__sidebar-user > i {
  color: var(--om-primary);
  font-size: 1.5rem;
}

.app-shell__sidebar-user div {
  display: grid;
  min-width: 0;
}

.app-shell__sidebar-user strong {
  font-size: 0.8125rem;
}

.app-shell__sidebar-user span {
  color: var(--om-neutral-600);
  font-size: 0.75rem;
}

.app-shell__main {
  width: 100%;
  min-width: 0;
  max-width: 100%;
}

.app-shell__content {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding-bottom: calc(var(--om-bottomnav-height) + env(safe-area-inset-bottom, 0px) + 1rem);
}

@media (min-width: 992px) {
  .app-shell {
    display: flex;
  }

  .app-shell__sidebar {
    display: flex;
    position: sticky;
    top: 0;
  }

  .app-shell__content {
    padding-bottom: 0;
  }

  .app-shell__bottom-navigation {
    display: none;
  }
}
</style>