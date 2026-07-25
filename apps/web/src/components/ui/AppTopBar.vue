<template>
  <header class="app-top-bar">
    <div class="app-top-bar__mobile om-safe-top">
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

    <div class="app-top-bar__desktop">
      <div class="app-top-bar__desktop-copy">
        <span>{{ eyebrow }}</span>
        <strong>{{ title }}</strong>
      </div>
      <div class="app-top-bar__desktop-actions">
        <LanguageSelector :show-label="false" compact />
        <div class="dropdown">
          <button class="btn btn-outline-secondary app-top-bar__desktop-account" type="button" data-bs-toggle="dropdown">
            <i class="bi bi-person-circle"></i>
            <span>{{ userName || accountLabel }}</span>
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

.app-top-bar__mobile,
.app-top-bar__desktop {
  align-items: center;
  justify-content: space-between;
  gap: var(--om-space-sm);
}

.app-top-bar__mobile {
  display: flex;
  min-height: var(--om-mobile-topbar-height);
  padding: 0.5rem max(1rem, env(safe-area-inset-right, 0px)) 0.5rem max(1rem, env(safe-area-inset-left, 0px));
}

.app-top-bar__identity,
.app-top-bar__actions,
.app-top-bar__desktop-actions {
  display: flex;
  align-items: center;
}

.app-top-bar__identity {
  min-width: 0;
  gap: 0.75rem;
}

.app-top-bar__actions,
.app-top-bar__desktop-actions {
  flex: 0 0 auto;
  gap: 0.5rem;
}

.app-top-bar__mark,
.app-top-bar__account {
  display: inline-flex;
  width: 2.75rem;
  height: 2.75rem;
  align-items: center;
  justify-content: center;
  border-radius: var(--om-radius-base);
}

.app-top-bar__mark {
  flex: 0 0 auto;
  background: var(--om-primary);
  color: #fff;
  font-size: 1.125rem;
}

.app-top-bar__account {
  border: 1px solid var(--om-neutral-300);
  background: var(--om-neutral-0);
  color: var(--om-primary);
  font-size: 1.3rem;
}

.app-top-bar__copy,
.app-top-bar__desktop-copy {
  display: grid;
  min-width: 0;
}

.app-top-bar__eyebrow,
.app-top-bar__desktop-copy span {
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

.app-top-bar__title,
.app-top-bar__desktop-copy strong {
  overflow: hidden;
  color: var(--om-neutral-900);
  font-size: 0.9375rem;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-top-bar__desktop {
  display: none;
  min-height: var(--om-topbar-height);
  padding: 0.75rem clamp(1.5rem, 3vw, 2.5rem);
}

.app-top-bar__desktop-account {
  display: inline-flex;
  min-height: 2.75rem;
  align-items: center;
  gap: 0.5rem;
  max-width: 18rem;
  overflow: hidden;
}

.app-top-bar__desktop-account span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (min-width: 992px) {
  .app-top-bar__mobile {
    display: none;
  }

  .app-top-bar__desktop {
    display: flex;
  }
}
</style>