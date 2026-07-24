<template>
  <div class="page-header" :class="{ 'page-header--compact': compact }">
    <div class="page-header-start">
      <button
        v-if="showBack"
        class="page-header-back"
        :aria-label="backLabel"
        @click="$emit('back')"
      >
        <i class="bi bi-arrow-left"></i>
      </button>

      <div>
        <div v-if="kicker" class="om-text-label">
          {{ kicker }}
        </div>
        <h1 class="page-header-title">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="page-header-subtitle">
          {{ subtitle }}
        </p>
      </div>
    </div>

    <div v-if="$slots.actions || (actions && actions.length)" class="page-header-actions">
      <slot name="actions">
        <button
          v-for="action in actions"
          :key="action.label"
          class="btn"
          :class="action.variant === 'primary' ? 'btn-primary' : 'btn-outline-secondary'"
          :disabled="action.disabled"
          @click="action.onClick"
        >
          <i v-if="action.icon" class="bi" :class="action.icon" style="margin-right: 6px"></i>
          {{ action.label }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface PageHeaderAction {
  label: string
  onClick: () => void
  icon?: string
  variant?: 'primary' | 'secondary'
  disabled?: boolean
}

defineProps<{
  title: string
  subtitle?: string
  kicker?: string
  showBack?: boolean
  backLabel?: string
  compact?: boolean
  actions?: PageHeaderAction[]
}>()

defineEmits<{
  (e: 'back'): void
}>()
</script>

<style scoped>
.page-header {
  display: flex;
  flex-direction: column;
  gap: var(--om-space-base);
  padding: var(--om-space-base);
}

@media (min-width: 768px) {
  .page-header {
    flex-direction: row;
    align-items: flex-start;
    justify-content: space-between;
    padding: var(--om-space-lg) var(--om-space-xl);
  }
}

.page-header--compact {
  padding: var(--om-space-sm) var(--om-space-base);
}

.page-header--compact .page-header-title {
  font-size: 1.25rem;
}

.page-header-start {
  display: flex;
  align-items: flex-start;
  gap: var(--om-space-sm);
  min-width: 0;
}

.page-header-back {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  color: var(--om-neutral-700);
  border-radius: var(--om-radius-base);
  cursor: pointer;
  flex-shrink: 0;
  transition: background-color var(--om-transition-fast);
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.page-header-back:hover {
  background: var(--om-neutral-100);
}

.page-header-back i {
  font-size: 1.25rem;
}

.page-header-title {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--om-neutral-900);
  margin: 0;
}

@media (min-width: 768px) {
  .page-header-title {
    font-size: 2rem;
  }
}

.page-header-subtitle {
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--om-neutral-500);
  margin: 4px 0 0;
  max-width: 600px;
}

.page-header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--om-space-sm);
  flex-shrink: 0;
}

.page-header-actions .btn {
  white-space: nowrap;
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
  border-radius: var(--om-radius-base);
  display: inline-flex;
  align-items: center;
}
</style>
