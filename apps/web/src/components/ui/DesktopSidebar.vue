<template>
  <aside :class="['desktop-sidebar', sidebarClass]">
    <div class="desktop-sidebar__brand">
      <i class="bi" :class="icon" aria-hidden="true"></i>
      <span>{{ title }}</span>
    </div>

    <nav class="desktop-sidebar__navigation">
      <section v-for="section in navigation" :key="section.label">
        <div class="desktop-sidebar__label">{{ section.label }}</div>
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

    <div class="desktop-sidebar__account">
      <div class="desktop-sidebar__user">
        <i class="bi bi-person-circle" aria-hidden="true"></i>
        <div>
          <strong>{{ authStore.user?.display_name }}</strong>
          <span>{{ authStore.user?.email }}</span>
        </div>
      </div>
      <button class="btn btn-outline-secondary w-100" @click="emit('logout')">
        <i class="bi bi-box-arrow-right"></i>
        <span>{{ localeStore.t('layout.signOut') }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import type { NavSection } from '@/composables/useRoleNavigation'

const props = withDefaults(defineProps<{
  title: string
  icon: string
  navigation: NavSection[]
  sidebarClass?: string
}>(), {
  sidebarClass: '',
})

const emit = defineEmits<{
  logout: []
}>()

const route = useRoute()
const authStore = useAuthStore()
const localeStore = useLocaleStore()

function isActive(destination: string) {
  return route.path === destination
    || (destination !== '/dashboard' && destination !== '/admin' && route.path.startsWith(`${destination}/`))
}
</script>

<style scoped>
.desktop-sidebar {
  display: flex;
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

.desktop-sidebar__brand {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  color: var(--om-neutral-900);
  font-weight: 750;
}

.desktop-sidebar__brand i {
  display: inline-grid;
  width: 2.25rem;
  height: 2.25rem;
  flex: 0 0 auto;
  place-items: center;
  border-radius: var(--om-radius-base);
  background: var(--om-primary-subtle);
  color: var(--om-primary);
}

.desktop-sidebar__brand span,
.desktop-sidebar__user strong,
.desktop-sidebar__user span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.desktop-sidebar__navigation {
  display: grid;
  gap: 1.25rem;
}

.desktop-sidebar__navigation section {
  display: grid;
  gap: 0.25rem;
}

.desktop-sidebar__label {
  padding-inline: 0.75rem;
  color: var(--om-neutral-600);
  font-size: 0.6875rem;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.desktop-sidebar__navigation :deep(.sidebar-link) {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.625rem;
}

.desktop-sidebar__navigation :deep(.sidebar-link span) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.desktop-sidebar__account {
  display: grid;
  gap: 0.75rem;
  margin-top: auto;
  padding-top: 1rem;
  border-top: 1px solid var(--om-neutral-200);
}

.desktop-sidebar__user {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 0.625rem;
}

.desktop-sidebar__user > i {
  color: var(--om-primary);
  font-size: 1.5rem;
}

.desktop-sidebar__user div {
  display: grid;
  min-width: 0;
}

.desktop-sidebar__user strong {
  font-size: 0.8125rem;
}

.desktop-sidebar__user span {
  color: var(--om-neutral-600);
  font-size: 0.75rem;
}

@media (max-width: 767px) {
  .desktop-sidebar {
    display: none !important;
  }
}
</style>
