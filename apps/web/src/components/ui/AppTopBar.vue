<template>
  <header class="app-top-bar om-safe-top">
    <div class="app-top-bar__inner">
      <div class="app-top-bar__identity">
        <span class="app-top-bar__mark" aria-hidden="true">
          <i class="bi" :class="icon"></i>
        </span>
        <div class="app-top-bar__copy">
          <span class="app-top-bar__eyebrow">{{ eyebrow }}</span>
          <strong class="app-top-bar__title">{{ title }}</strong>
        </div>
      </div>
      <div class="app-top-bar__actions">
        <LanguageSelector :show-label="false" compact />
        <NotificationBell />
        <div class="dropdown">
          <button
            class="app-top-bar__account"
            type="button"
            data-bs-toggle="dropdown"
            :aria-label="accountLabel"
          >
            <i class="bi bi-person-circle"></i>
          </button>
          <ul class="dropdown-menu dropdown-menu-end shadow-sm">
            <li><h6 class="dropdown-header">{{ signedInAsLabel }}</h6></li>
            <li><span class="dropdown-item-text small text-muted text-break">{{ userEmail }}</span></li>
            <li><hr class="dropdown-divider" /></li>
            <li><RouterLink to="/account/security" class="dropdown-item">{{ accountSecurityLabel }}</RouterLink></li>
            <li><button class="dropdown-item text-danger" @click="$emit('logout')">{{ signOutLabel }}</button></li>
          </ul>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import LanguageSelector from '@/components/LanguageSelector.vue'
import NotificationBell from '@/components/ui/NotificationBell.vue'

defineProps<{
  eyebrow: string
  title: string
  icon: string
  userName?: string
  userEmail?: string
  accountLabel: string
  accountSecurityLabel: string
  signedInAsLabel: string
  signOutLabel: string
}>()

defineEmits<{
  logout: []
}>()
</script>

<style scoped>
.app-top-bar {
  position: sticky;
  top: 0;
  z-index: 1020;
  background: var(--om-neutral-0);
  border-bottom: 1px solid var(--om-neutral-200);
}

.app-top-bar__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--om-space-sm);
  width: 100%;
  max-width: var(--om-content-max-width);
  margin: 0 auto;
  min-height: var(--om-topbar-height);
  padding: 0 max(1rem, env(safe-area-inset-right, 0px)) 0 max(1rem, env(safe-area-inset-left, 0px));
}

.app-top-bar__identity {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  min-width: 0;
  flex: 1 1 auto;
}

.app-top-bar__mark {
  display: inline-flex;
  width: 2.5rem;
  height: 2.5rem;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  border-radius: var(--om-radius-base);
  background: var(--om-primary);
  color: #fff;
  font-size: 1.0625rem;
}

.app-top-bar__copy {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.app-top-bar__eyebrow {
  overflow: hidden;
  color: var(--om-neutral-600);
  font-size: 0.6875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  line-height: 1.25;
  text-overflow: ellipsis;
  text-transform: uppercase;
  white-space: nowrap;
}

.app-top-bar__title {
  overflow: hidden;
  color: var(--om-neutral-900);
  font-size: 0.9375rem;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 40vw;
}

.app-top-bar__actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 0 0 auto;
}

.app-top-bar__account {
  display: inline-flex;
  width: 2.75rem;
  height: 2.75rem;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--om-neutral-300);
  border-radius: var(--om-radius-base);
  background: var(--om-neutral-0);
  color: var(--om-primary);
  font-size: 1.3rem;
}

@media (min-width: 768px) {
  .app-top-bar__title {
    max-width: 30rem;
  }
}
</style>
