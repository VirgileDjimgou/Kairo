<template>
  <nav
    class="bottom-nav om-fixed-bottom-safe"
    role="navigation"
    :aria-label="ariaLabel"
  >
    <button
      v-for="item in visibleItems"
      :key="item.id"
      class="bottom-nav-item"
      :class="{ active: item.active }"
      :aria-label="item.label"
      :aria-current="item.active ? 'page' : undefined"
      @click="$emit('navigate', item.id)"
    >
      <span class="bottom-nav-icon" aria-hidden="true">
        <i class="bi" :class="item.icon"></i>
      </span>
      <span class="bottom-nav-label">{{ item.label }}</span>

      <span v-if="item.badge" class="bottom-nav-badge">
        {{ item.badge > 99 ? '99+' : item.badge }}
      </span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface BottomNavItem {
  id: string
  label: string
  icon: string
  active: boolean
  badge?: number
  route?: string
}

const props = defineProps<{
  items: BottomNavItem[]
  maxItems?: number
  ariaLabel?: string
}>()

defineEmits<{
  (e: 'navigate', id: string): void
}>()

const visibleItems = computed(() => {
  const max = props.maxItems ?? 5
  return props.items.slice(0, max)
})
</script>

<style scoped>
.bottom-nav {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  width: 100%;
  min-height: calc(var(--om-bottomnav-height) + env(safe-area-inset-bottom, 0px));
  padding: 0.25rem max(0.25rem, env(safe-area-inset-right, 0px)) env(safe-area-inset-bottom, 0px) max(0.25rem, env(safe-area-inset-left, 0px));
  background: var(--om-neutral-0);
  border-top: 1px solid var(--om-neutral-300);
  box-shadow: 0 -0.25rem 1rem rgba(30, 34, 40, 0.08);
  z-index: 1040;
}

.bottom-nav-item {
  display: flex;
  min-width: 0;
  min-height: 4rem;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.125rem;
  border: none;
  background: transparent;
  color: var(--om-neutral-600);
  cursor: pointer;
  padding: 0.25rem 0.125rem;
  border-radius: var(--om-radius-sm);
  position: relative;
  transition: background-color var(--om-transition-fast), color var(--om-transition-fast);
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.bottom-nav-icon {
  display: inline-grid;
  width: 1.5rem;
  height: 1.5rem;
  place-items: center;
  border-radius: var(--om-radius-sm);
}

.bottom-nav-icon i {
  font-size: 1.25rem;
  line-height: 1;
}

.bottom-nav-item.active {
  color: var(--om-primary);
  font-weight: 700;
}

.bottom-nav-item.active .bottom-nav-icon {
  background: var(--om-primary-subtle);
}

.bottom-nav-label {
  max-width: 100%;
  font-size: 0.625rem;
  font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
}

.bottom-nav-badge {
  position: absolute;
  top: 0.125rem;
  right: 15%;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  background: #df3c35;
  color: #fff;
  font-size: 0.6875rem;
  font-weight: 600;
  line-height: 18px;
  text-align: center;
  padding: 0 4px;
}
</style>
