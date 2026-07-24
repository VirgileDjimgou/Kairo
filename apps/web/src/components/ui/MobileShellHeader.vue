<template>
  <header class="mobile-shell-header om-safe-top">
    <div class="mobile-shell-header__identity">
      <span class="mobile-shell-header__mark" aria-hidden="true">
        <i class="bi" :class="icon"></i>
      </span>
      <div class="mobile-shell-header__copy">
        <span class="mobile-shell-header__eyebrow">{{ eyebrow }}</span>
        <strong class="mobile-shell-header__title">{{ title }}</strong>
      </div>
    </div>

    <div class="mobile-shell-header__actions">
      <slot name="actions" />
      <button
        class="mobile-shell-header__menu"
        type="button"
        :aria-label="menuLabel"
        @click="$emit('openMenu')"
      >
        <i class="bi bi-list"></i>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  eyebrow: string
  title: string
  icon: string
  menuLabel: string
}>()

defineEmits<{
  openMenu: []
}>()
</script>

<style scoped>
.mobile-shell-header {
  position: sticky;
  top: 0;
  z-index: 1020;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 4.5rem;
  padding: 0.75rem 1rem;
  background: color-mix(in srgb, var(--om-neutral-0) 94%, transparent);
  border-bottom: 1px solid var(--om-neutral-200);
  backdrop-filter: blur(14px);
}

.mobile-shell-header__identity,
.mobile-shell-header__actions {
  display: flex;
  align-items: center;
}

.mobile-shell-header__identity {
  min-width: 0;
  gap: 0.75rem;
}

.mobile-shell-header__actions {
  flex-shrink: 0;
  gap: 0.375rem;
}

.mobile-shell-header__mark,
.mobile-shell-header__menu {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.625rem;
  height: 2.625rem;
  border-radius: 0.875rem;
}

.mobile-shell-header__mark {
  flex: 0 0 auto;
  background: var(--om-primary);
  color: #fff;
  font-size: 1.125rem;
}

.mobile-shell-header__copy {
  display: grid;
  min-width: 0;
}

.mobile-shell-header__eyebrow {
  overflow: hidden;
  color: var(--om-neutral-600);
  font-size: 0.625rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  line-height: 1.25;
  text-overflow: ellipsis;
  text-transform: uppercase;
  white-space: nowrap;
}

.mobile-shell-header__title {
  overflow: hidden;
  color: var(--om-neutral-900);
  font-size: 0.9375rem;
  letter-spacing: -0.015em;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mobile-shell-header__menu {
  border: 1px solid var(--om-neutral-200);
  background: var(--om-neutral-0);
  color: var(--om-neutral-900);
  font-size: 1.25rem;
}

.mobile-shell-header__menu:active {
  transform: scale(0.96);
}
</style>
