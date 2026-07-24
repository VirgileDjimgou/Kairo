<template>
  <div
    class="app-button"
    :class="[`app-button--${variant}`, `app-button--${size}`, { 'app-button--block': block, 'app-button--loading': loading, 'app-button--icon-only': iconOnly }]"
    :disabled="disabled || loading"
    :type="type"
    :aria-busy="loading"
    :aria-label="iconOnly ? ariaLabel : undefined"
    v-bind="$attrs"
  >
    <span v-if="loading" class="app-button-spinner om-spin">
      <i class="bi bi-arrow-repeat"></i>
    </span>
    <i v-else-if="icon" class="bi" :class="icon"></i>
    <span v-if="!iconOnly" class="app-button-label">
      <slot />
    </span>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  block?: boolean
  loading?: boolean
  disabled?: boolean
  icon?: string
  iconOnly?: boolean
  ariaLabel?: string
  type?: 'button' | 'submit' | 'reset'
}>(), {
  variant: 'primary',
  size: 'md',
  type: 'button',
})
</script>

<style scoped>
.app-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid transparent;
  border-radius: var(--om-radius-base);
  font-weight: 500;
  cursor: pointer;
  transition:
    background-color var(--om-transition-fast),
    color var(--om-transition-fast),
    border-color var(--om-transition-fast),
    opacity var(--om-transition-fast);
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
  white-space: nowrap;
  text-decoration: none;
  user-select: none;
}

.app-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.app-button--sm {
  font-size: 0.8125rem;
  padding: 0.375rem 0.75rem;
  min-height: 36px;
}

.app-button--md {
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
  min-height: 44px;
}

.app-button--lg {
  font-size: 0.9375rem;
  padding: 0.625rem 1.25rem;
  min-height: 48px;
}

.app-button--block {
  width: 100%;
}

.app-button--primary {
  background: var(--om-primary);
  border-color: var(--om-primary);
  color: #fff;
}

.app-button--primary:hover:not(:disabled) {
  background: var(--om-primary-hover);
  border-color: var(--om-primary-hover);
}

.app-button--secondary {
  background: var(--om-neutral-100);
  border-color: var(--om-neutral-200);
  color: var(--om-neutral-700);
}

.app-button--secondary:hover:not(:disabled) {
  background: var(--om-neutral-200);
  border-color: var(--om-neutral-300);
}

.app-button--danger {
  background: var(--om-danger);
  border-color: var(--om-danger);
  color: #fff;
}

.app-button--danger:hover:not(:disabled) {
  background: #b32424;
  border-color: #b32424;
}

.app-button--ghost {
  background: transparent;
  border-color: transparent;
  color: var(--om-neutral-700);
}

.app-button--ghost:hover:not(:disabled) {
  background: var(--om-neutral-100);
}

.app-button--outline {
  background: transparent;
  border-color: var(--om-neutral-300);
  color: var(--om-neutral-700);
}

.app-button--outline:hover:not(:disabled) {
  background: var(--om-neutral-50);
  border-color: var(--om-neutral-400);
}

.app-button--icon-only {
  padding: 0;
}

.app-button--icon-only.app-button--sm {
  width: 36px;
  height: 36px;
}

.app-button--icon-only.app-button--md {
  width: 44px;
  height: 44px;
}

.app-button--icon-only.app-button--lg {
  width: 48px;
  height: 48px;
}

.app-button--icon-only i {
  font-size: 1.25rem;
  margin: 0;
}

.app-button--loading {
  cursor: wait;
}

.app-button-spinner {
  display: inline-flex;
  align-items: center;
}

.app-button-spinner i {
  font-size: 1rem;
}

.app-button-label {
  line-height: 1.35;
}
</style>
