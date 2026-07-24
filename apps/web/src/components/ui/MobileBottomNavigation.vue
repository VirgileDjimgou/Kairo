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
      <i class="bi" :class="item.icon"></i>
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
  display: flex;
  left: max(0.75rem, env(safe-area-inset-left, 0px));
  right: max(0.75rem, env(safe-area-inset-right, 0px));
  bottom: max(0.75rem, env(safe-area-inset-bottom, 0px));
  height: 4.5rem;
  padding: 0.375rem;
  background: #14233a;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 1.375rem;
  box-shadow: 0 0.75rem 1.75rem rgba(15, 33, 56, 0.22);
  z-index: 1040;
}

.bottom-nav-item {
  flex: 1;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.1875rem;
  min-width: 48px;
  min-height: 3.5rem;
  border: none;
  background: transparent;
  color: rgba(255, 255, 255, 0.68);
  cursor: pointer;
  padding: 0.375rem 0.25rem;
  border-radius: 1rem;
  position: relative;
  transition: background-color var(--om-transition-fast), color var(--om-transition-fast), transform var(--om-transition-fast);
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.bottom-nav-item i {
  font-size: 1.25rem;
  line-height: 1;
}

.bottom-nav-item.active {
  background: #fff;
  color: var(--om-primary);
  font-weight: 700;
}

.bottom-nav-item:active {
  transform: scale(0.96);
}

.bottom-nav-label {
  font-size: 0.625rem;
  font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.bottom-nav-badge {
  position: absolute;
  top: 0.25rem;
  right: calc(50% - 1.125rem);
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
