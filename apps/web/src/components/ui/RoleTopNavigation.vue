<template>
  <nav ref="navigationElement" class="role-top-navigation" :aria-label="label">
    <RouterLink
      v-for="item in items"
      :key="item.to"
      :to="item.to"
      class="role-top-navigation__tab"
      :class="{ 'role-top-navigation__tab--active': isActive(item.to) }"
      :aria-current="isActive(item.to) ? 'page' : undefined"
      :data-route="item.to"
    >
      <i class="bi" :class="item.icon" aria-hidden="true"></i>
      <span>{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import type { NavItem } from '@/composables/useRoleNavigation'

const props = defineProps<{
  items: NavItem[]
  label: string
}>()

const route = useRoute()
const navigationElement = ref<HTMLElement | null>(null)

function isActive(destination: string) {
  return route.path === destination
    || (destination !== '/dashboard' && destination !== '/admin' && route.path.startsWith(`${destination}/`))
}

async function revealActiveTab() {
  await nextTick()
  const activeTab = navigationElement.value?.querySelector<HTMLElement>('[aria-current="page"]')
  activeTab?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
}

watch(() => route.fullPath, revealActiveTab)
watch(() => props.items, revealActiveTab, { deep: true })
onMounted(revealActiveTab)
</script>

<style scoped>
.role-top-navigation {
  position: sticky;
  top: var(--om-mobile-topbar-height);
  z-index: 1010;
  display: flex;
  min-width: 0;
  gap: 0.5rem;
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  padding: 0.5rem max(1rem, env(safe-area-inset-right, 0px)) 0.625rem max(1rem, env(safe-area-inset-left, 0px));
  background: var(--om-neutral-0);
  border-bottom: 1px solid var(--om-neutral-200);
  scrollbar-width: none;
  scroll-padding-inline: 1rem;
  scroll-snap-type: inline proximity;
}

.role-top-navigation::-webkit-scrollbar {
  display: none;
}

.role-top-navigation__tab {
  display: inline-flex;
  flex: 0 0 auto;
  min-height: 2.75rem;
  align-items: center;
  gap: 0.4375rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid transparent;
  border-radius: var(--om-radius-base);
  color: var(--om-neutral-700);
  font-size: 0.8125rem;
  font-weight: 650;
  line-height: 1.2;
  scroll-snap-align: center;
  text-decoration: none;
  white-space: nowrap;
}

.role-top-navigation__tab i {
  font-size: 1rem;
}

.role-top-navigation__tab--active {
  border-color: color-mix(in srgb, var(--om-primary) 22%, var(--om-neutral-200));
  background: var(--om-primary-subtle);
  color: var(--om-primary);
}

@media (min-width: 768px) {
  .role-top-navigation {
    padding-inline: clamp(1.5rem, 3vw, 2.5rem);
  }
}
</style>
