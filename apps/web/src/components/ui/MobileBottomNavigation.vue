<template>
  <nav
    class="bottom-nav om-fixed-bottom-safe"
    role="navigation"
    aria-label="Mobile navigation"
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
  background: var(--om-neutral-0);
  border-top: 1px solid var(--om-neutral-200);
  height: var(--om-bottomnav-height);
  padding-bottom: env(safe-area-inset-bottom, 0px);
  z-index: 1040;
}

.bottom-nav-item {
  flex: 1;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  min-width: 48px;
  min-height: 48px;
  border: none;
  background: transparent;
  color: var(--om-neutral-500);
  cursor: pointer;
  padding: 0 var(--om-space-sm);
  position: relative;
  transition: color var(--om-transition-fast);
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.bottom-nav-item i {
  font-size: 1.375rem;
  line-height: 1;
}

.bottom-nav-item.active {
  color: var(--om-primary);
}

.bottom-nav-item.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 3px;
  background: var(--om-primary);
  border-radius: 0 0 3px 3px;
}

.bottom-nav-label {
  font-size: 0.6875rem;
  font-weight: 500;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.bottom-nav-badge {
  position: absolute;
  top: 4px;
  right: calc(50% - 18px);
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background: var(--om-danger);
  color: #fff;
  font-size: 0.6875rem;
  font-weight: 600;
  line-height: 18px;
  text-align: center;
  padding: 0 4px;
}
</style>
